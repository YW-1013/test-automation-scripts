<#
collect_drivers.ps1  —— 在【目标Windows设备】上运行的驱动信息采集器
================================================================
作用：把目标机上的驱动信息（设备->活动驱动版本、是否签名、INF包签名者、异常设备、商店应用）
      导出成一个 driver_collect.json，拿回来交给 verify_drivers.py 做比对判断。

特点：
  - 纯 PowerShell，目标机无需安装 Python / 任何依赖。
  - pnputil 解析不依赖系统语言；扩展类INF(多一行 Extension ID)会用“值=日期+版本”定位版本行，避免错位。
  - 建议以管理员身份运行（部分驱动/设备信息、-AllUsers 应用列表需要提权才完整）。

用法（在目标机上）：
  powershell -ExecutionPolicy Bypass -File .\collect_drivers.ps1
  可选指定输出： -Out D:\xxx\driver_collect.json
#>
param(
    [string]$Out = "$PSScriptRoot\driver_collect.json"
)

$ErrorActionPreference = 'SilentlyContinue'
Write-Host "[采集] 开始采集驱动信息..." -ForegroundColor Cyan

# ---------- 1. 已安装驱动：设备 -> 活动驱动版本 + 是否签名 ----------
$signed = Get-CimInstance Win32_PnPSignedDriver |
    Where-Object { $_.DeviceName } |
    ForEach-Object {
        [pscustomobject]@{
            DeviceName = $_.DeviceName
            Version    = $_.DriverVersion
            Provider   = $_.DriverProviderName
            IsSigned   = [bool]$_.IsSigned
            Signer     = $_.Signer
            Class      = $_.DeviceClass
            DeviceID   = $_.DeviceID
            InfName    = $_.InfName
            DriverDate = if ($_.DriverDate) { $_.DriverDate.ToString('yyyy-MM-dd') } else { $null }
        }
    }
Write-Host ("[采集] 已安装驱动条目: {0}" -f $signed.Count)

# ---------- 2. pnputil /enum-drivers：OEM INF 包 + 签名者(Signer Name) ----------
$infRaw = (pnputil /enum-drivers) -join "`n"
$infPackages = @()
foreach ($block in ($infRaw -split "`n\s*`n")) {
    $lines = $block -split "`n" | Where-Object { $_ -match ':' }
    if ($lines.Count -lt 7) { continue }
    # 取每行第一个冒号后的值
    $vals = $lines | ForEach-Object { ($_ -split ':', 2)[1].Trim() }
    $published = $vals[0]
    if ($published -notmatch '\.inf$') { continue }   # 跳过标题块等非驱动块
    # 前4项(发布名/原始名/提供者/类)位置稳定；但【扩展类INF会多一行 Extension ID】，
    # 会把 Driver Version / Signer 往后顶一位。故按“值=日期+版本”定位版本行，签名者=其下一行，避免错位。
    $verIdx = -1
    for ($k = 4; $k -lt $vals.Count; $k++) {
        if ($vals[$k] -match '^\d{1,2}/\d{1,2}/\d{4}\s+\S+') { $verIdx = $k; break }
    }
    if ($verIdx -ge 0) {
        $verToken = ($vals[$verIdx] -split '\s+')[-1]
        $signer   = if ($verIdx + 1 -lt $vals.Count) { $vals[$verIdx + 1] } else { '' }
    } else {
        $verToken = ($vals[5] -split '\s+')[-1]; $signer = $vals[6]   # 兜底(理论上不会走到)
    }
    $infPackages += [pscustomobject]@{
        PublishedName = $published
        OriginalName  = $vals[1]
        Provider      = $vals[2]
        Class         = $vals[3]
        Version       = $verToken
        Signer        = $signer
    }
}
Write-Host ("[采集] OEM INF 包: {0}" -f $infPackages.Count)

# ---------- 3. 异常设备（黄感/未启动/无驱动等）ConfigManagerErrorCode != 0 ----------
$cmErr = @{
    1='设备未正确配置'; 3='驱动损坏或内存不足'; 10='设备无法启动'; 12='资源不足';
    14='需重启'; 18='需重装驱动'; 19='注册表损坏'; 21='系统正在移除'; 22='设备被禁用';
    24='设备不存在/未挂载'; 28='未安装驱动程序'; 31='工作不正常(驱动加载失败)';
    32='驱动被禁用启动'; 33='硬件资源冲突'; 37='驱动初始化失败'; 39='驱动损坏/丢失';
    43='驱动报告设备故障已停止'; 45='设备当前未连接'; 48='驱动被阻止启动'; 52='无法验证驱动签名'
}
$problems = Get-CimInstance Win32_PnPEntity |
    Where-Object { $_.ConfigManagerErrorCode -and $_.ConfigManagerErrorCode -ne 0 } |
    ForEach-Object {
        $code = [int]$_.ConfigManagerErrorCode
        [pscustomobject]@{
            Name      = $_.Name
            DeviceID  = $_.DeviceID
            Class     = $_.PNPClass
            Present   = [bool]$_.Present
            ErrorCode = $code
            ErrorText = if ($cmErr.ContainsKey($code)) { $cmErr[$code] } else { "未知错误码$code" }
        }
    }
$problemsPresent = @($problems | Where-Object { $_.Present })
Write-Host ("[采集] 异常设备(在位): {0}" -f $problemsPresent.Count) -ForegroundColor Yellow

# ---------- 4. 商店(UWP)应用：部分“驱动清单项”其实是Store应用(如 Realtek Audio Control / Intel Graphics Software) ----------
# 这些应用不会出现在驱动/INF枚举里，需用 Get-AppxPackage 单独采集，供 verify 端核对。
# -AllUsers 需要管理员权限；非管理员时回退到当前用户范围。
$apps = @(Get-AppxPackage -AllUsers -ErrorAction SilentlyContinue |
    Where-Object { $_.Name } |
    ForEach-Object {
        [pscustomobject]@{
            Name            = $_.Name
            Publisher       = $_.Publisher
            Version         = if ($_.Version) { $_.Version.ToString() } else { $null }
            PackageFullName = $_.PackageFullName
        }
    })
if (-not $apps -or $apps.Count -eq 0) {
    $apps = @(Get-AppxPackage -ErrorAction SilentlyContinue |
        Where-Object { $_.Name } |
        ForEach-Object {
            [pscustomobject]@{
                Name            = $_.Name
                Publisher       = $_.Publisher
                Version         = if ($_.Version) { $_.Version.ToString() } else { $null }
                PackageFullName = $_.PackageFullName
            }
        })
}
Write-Host ("[采集] 商店(UWP)应用: {0}" -f $apps.Count)

# ---------- 汇总输出 ----------
$os = Get-CimInstance Win32_OperatingSystem
$result = [pscustomobject]@{
    meta = [pscustomobject]@{
        ComputerName = $env:COMPUTERNAME
        CollectedAt  = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        OSCaption    = $os.Caption
        OSBuild      = $os.BuildNumber
        IsAdmin      = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    signed_drivers   = $signed
    inf_packages     = $infPackages
    problems         = $problemsPresent
    problems_all     = $problems
    apps             = $apps
}

$result | ConvertTo-Json -Depth 6 | Out-File -FilePath $Out -Encoding utf8
Write-Host ("[采集] 完成 -> {0}" -f $Out) -ForegroundColor Green
if (-not $result.meta.IsAdmin) {
    Write-Host "[警告] 当前非管理员运行，部分信息可能不全，建议以管理员身份重跑。" -ForegroundColor Yellow
}
