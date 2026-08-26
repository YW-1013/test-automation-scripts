import sys
import time
from datetime import datetime, timedelta
import pytz
import uiautomator2 as u2
import logging
import os
import subprocess

time_zone = ['中国 - 北京(UTC+08:00)', '中国 - 台北(UTC+08:00)', '俄罗斯 - 伊尔库茨克(UTC+08:00)', '印度尼西亚 - 望加锡(UTC+08:00)',
             '文莱 - 文莱(UTC+08:00)', '新加坡 - 新加坡(UTC+08:00)', '澳大利亚 - 珀斯(UTC+08:00)', '菲律宾 - 马尼拉(UTC+08:00)',
             '蒙古 - 乔巴山/乌兰巴托(UTC+08:00)', '马来西亚 - 吉隆坡/古晋(UTC+08:00)', '澳大利亚 - 尤克拉(UTC+08:45)', '东帝汶 - 帝力(UTC+09:00)',
             '俄罗斯 - 赤塔/汉德加/雅库茨克(UTC+09:00)', '印度尼西亚 - 查亚普拉(UTC+09:00)', '帕劳 - 帕劳(UTC+09:00)', '日本 - 东京(UTC+09:00)',
             '朝鲜 - 平壤(UTC+09:00)', '韩国 - 首尔(UTC+09:00)', '澳大利亚 - 达尔文(UTC+09:30)', '俄罗斯 - 乌斯内拉/符拉迪沃斯托克(UTC+10:00)',
             '关岛 - 关岛(UTC+10:00)', '北马里亚纳群岛 - 塞班(UTC+10:00)', '南极洲 - 迪蒙·迪维尔(UTC+10:00)', '密克罗尼西亚 - 特鲁克群岛(UTC+10:00)',
             '巴布亚新几内亚 - 莫尔兹比港(UTC+10:00)', '澳大利亚 - 布里斯班/林德曼(UTC+10:00)', '澳大利亚 - 阿德莱德/布罗肯希尔(UTC+10:30)',
             '俄罗斯 - 马加丹/萨哈林(UTC+11:00)', '南极洲 - 卡塞(UTC+11:00)', '密克罗尼西亚 - 库赛埃/波纳佩岛(UTC+11:00)',
             '巴布亚新几内亚 - 布干维尔(UTC+11:00)', '所罗门群岛 - 瓜达尔卡纳尔(UTC+11:00)', '新喀里多尼亚 - 努美阿(UTC+11:00)',
             '澳大利亚 - 麦格理/悉尼(UTC+11:00)', '瓦努阿图 - 埃法特(UTC+11:00)', '俄罗斯 - 阿纳德尔/堪察加(UTC+12:00)', '图瓦卢 - 富纳富提(UTC+12:00)',
             '基里巴斯 - 塔拉瓦(UTC+12:00)', '斐济 - 斐济(UTC+12:00)', '瑙鲁 - 瑙鲁(UTC+12:00)', '瓦利斯和富图纳 - 瓦利斯(UTC+12:00)',
             '美国本土外小岛屿 - 威克(UTC+12:00)', '诺福克岛 - 诺福克(UTC+12:00)', '马绍尔群岛 - 夸贾林/马朱罗(UTC+12:00)',
             '南极洲 - 麦克默多/奥克兰(UTC+13:00)', '基里巴斯 - 恩德伯里(UTC+13:00)', '托克劳 - 法考福(UTC+13:00)', '新西兰 - 奥克兰(UTC+13:00)',
             '汤加 - 东加塔布(UTC+13:00)', '萨摩亚 - 阿皮亚(UTC+13:00)', '新西兰 - 查塔姆(UTC+13:45)', '基里巴斯 - 基里地马地岛(UTC+14:00)',
             '纽埃 - 纽埃(UTC-11:00)', '美国本土外小岛屿 - 中途岛(UTC-11:00)', '美属萨摩亚 - 帕果帕果(UTC-11:00)', '库克群岛 - 拉罗汤加(UTC-10:00)',
             '法属波利尼西亚 - 塔希提(UTC-10:00)', '美国 - 埃达克/檀香山(UTC-10:00)', '美国本土外小岛屿 - 约翰斯顿(UTC-10:00)',
             '法属波利尼西亚 - 马克萨斯(UTC-09:30)', '法属波利尼西亚 - 甘比尔(UTC-09:00)', '美国 - 安克雷奇/朱诺(UTC-09:00)', '加拿大 - 温哥华(UTC-08:00)',
             '墨西哥 - 蒂华纳/圣伊萨贝尔(UTC-08:00)', '皮特凯恩群岛 - 皮特凯恩(UTC-08:00)', '美国 - 洛杉矶(UTC-08:00)',
             '加拿大 - 剑桥湾/克雷斯顿(UTC-07:00)', '墨西哥 - 华雷斯城/埃莫西约(UTC-07:00)', '美国 - 博伊西/丹佛(UTC-07:00)',
             '伯利兹 - 伯利兹(UTC-06:00)', '加拿大 - 雷尼河/兰今湾(UTC-06:00)', '危地马拉 - 危地马拉(UTC-06:00)', '厄瓜多尔 - 加拉帕戈斯(UTC-06:00)',
             '哥斯达黎加 - 哥斯达黎加(UTC-06:00)', '墨西哥 - 巴伊亚班德拉斯/奇瓦瓦(UTC-06:00)', '尼加拉瓜 - 马那瓜(UTC-06:00)',
             '洪都拉斯 - 特古西加尔巴(UTC-06:00)', '美国 - 芝加哥/印第安纳州诺克斯(UTC-06:00)', '萨尔瓦多 - 萨尔瓦多(UTC-06:00)',
             '加拿大 - 阿蒂科肯/伊魁特(UTC-05:00)', '厄瓜多尔 - 瓜亚基尔(UTC-05:00)', '古巴 - 哈瓦那(UTC-05:00)', '哥伦比亚 - 波哥大(UTC-05:00)',
             '墨西哥 - 坎昆(UTC-05:00)', '巴哈马 - 拿骚(UTC-05:00)', '巴拿马 - 巴拿马(UTC-05:00)', '巴西 - 依伦尼贝/里奥布郎库(UTC-05:00)',
             '开曼群岛 - 开曼(UTC-05:00)', '智利 - 复活节岛(UTC-05:00)', '海地 - 太子港(UTC-05:00)', '牙买加 - 牙买加(UTC-05:00)',
             '特克斯和凯科斯群岛 - 大特克(UTC-05:00)', '秘鲁 - 利马(UTC-05:00)', '美国 - 底特律/印第安纳波利斯(UTC-05:00)',
             '加拿大 - 布兰克萨布隆/格莱斯贝(UTC-04:00)', '圣卢西亚 - 圣卢西亚(UTC-04:00)', '圣基茨和尼维斯 - 圣基茨(UTC-04:00)',
             '圣巴泰勒米 - 圣巴泰勒米岛(UTC-04:00)', '圣文森特和格林纳丁斯 - 圣文森特(UTC-04:00)', '圭亚那 - 圭亚那(UTC-04:00)',
             '多米尼克 - 多米尼加(UTC-04:00)', '多米尼加共和国 - 圣多明各(UTC-04:00)', '委内瑞拉 - 加拉加斯(UTC-04:00)', '安圭拉 - 安圭拉(UTC-04:00)',
             '安提瓜和巴布达 - 安提瓜(UTC-04:00)', '巴巴多斯 - 巴巴多斯(UTC-04:00)', '巴西 - 博阿维斯塔/大坎普(UTC-04:00)', '库拉索 - 库拉索(UTC-04:00)',
             '格林纳达 - 格林纳达(UTC-04:00)', '格陵兰 - 图勒(UTC-04:00)', '法属圣马丁 - 马里戈特(UTC-04:00)', '波多黎各 - 波多黎各(UTC-04:00)',
             '特立尼达和多巴哥 - 西班牙港(UTC-04:00)', '玻利维亚 - 拉巴斯(UTC-04:00)', '瓜德罗普 - 瓜德罗普(UTC-04:00)', '百慕大 - 百慕大(UTC-04:00)',
             '美属维尔京群岛 - 圣托马斯(UTC-04:00)', '英属维尔京群岛 - 托尔托拉(UTC-04:00)', '荷属加勒比区 - 克拉伦代克(UTC-04:00)',
             '荷属圣马丁 - 下太子区(UTC-04:00)', '蒙特塞拉特 - 蒙特塞拉特(UTC-04:00)', '阿鲁巴 - 阿鲁巴(UTC-04:00)', '马提尼克 - 马提尼克(UTC-04:00)',
             '加拿大 - 圣约翰斯(UTC-03:30)', '乌拉圭 - 蒙得维的亚(UTC-03:00)', '南极洲 - 帕尔默/罗瑟拉(UTC-03:00)',
             '圣皮埃尔和密克隆群岛 - 密克隆(UTC-03:00)', '巴拉圭 - 亚松森(UTC-03:00)', '巴西 - 阿拉瓜伊纳/巴伊亚(UTC-03:00)',
             '智利 - 蓬塔阿雷纳斯/圣地亚哥(UTC-03:00)', '法属圭亚那 - 卡宴(UTC-03:00)', '福克兰群岛（马尔维纳斯群岛） - 斯坦利(UTC-03:00)',
             '苏里南 - 帕拉马里博(UTC-03:00)', '阿根廷 - 布宜诺斯艾利斯/卡塔马卡(UTC-03:00)', '南乔治亚和南桑威奇群岛 - 南乔治亚(UTC-02:00)',
             '巴西 - 洛罗尼亚(UTC-02:00)', '格陵兰 - 努克(UTC-02:00)', '佛得角 - 佛得角(UTC-01:00)', '格陵兰 - 斯科列斯比桑德(UTC-01:00)',
             '葡萄牙 - 亚速尔群岛(UTC-01:00)', '冈比亚 - 班珠尔(UTC+00:00)', '冰岛 - 雷克雅未克(UTC+00:00)', '几内亚 - 科纳克里(UTC+00:00)',
             '几内亚比绍 - 比绍(UTC+00:00)', '利比里亚 - 蒙罗维亚(UTC+00:00)', '加纳 - 阿克拉(UTC+00:00)', '南极洲 - 特罗尔(UTC+00:00)',
             '圣多美和普林西比 - 圣多美(UTC+00:00)', '圣赫勒拿 - 圣赫勒拿(UTC+00:00)', '塞内加尔 - 达喀尔(UTC+00:00)', '塞拉利昂 - 弗里敦(UTC+00:00)',
             '多哥 - 洛美(UTC+00:00)', '布基纳法索 - 瓦加杜古(UTC+00:00)', '根西岛 - 根西岛(UTC+00:00)', '格陵兰 - 丹马沙文(UTC+00:00)',
             '毛里塔尼亚 - 努瓦克肖特(UTC+00:00)', '法罗群岛 - 法罗(UTC+00:00)', '泽西岛 - 泽西岛(UTC+00:00)', '爱尔兰 - 都柏林(UTC+00:00)',
             '科特迪瓦 - 阿比让/雷克雅未克(UTC+00:00)', '英国 - 伦敦(UTC+00:00)', '葡萄牙 - 马德拉/里斯本(UTC+00:00)', '西班牙 - 加那利(UTC+00:00)',
             '马恩岛 - 马恩岛(UTC+00:00)', '马里 - 巴马科(UTC+00:00)', '中非共和国 - 班吉(UTC+01:00)', '丹麦 - 哥本哈根(UTC+01:00)',
             '乍得 - 恩贾梅纳(UTC+01:00)', '克罗地亚 - 萨格勒布(UTC+01:00)', '列支敦士登 - 瓦杜兹(UTC+01:00)', '刚果（布） - 布拉柴维尔(UTC+01:00)',
             '刚果（金） - 金沙萨(UTC+01:00)', '加蓬 - 利伯维尔(UTC+01:00)', '匈牙利 - 布达佩斯(UTC+01:00)', '北马其顿 - 斯科普里(UTC+01:00)',
             '卢森堡 - 卢森堡(UTC+01:00)', '喀麦隆 - 杜阿拉(UTC+01:00)', '圣马力诺 - 圣马力诺(UTC+01:00)', '塞尔维亚 - 贝尔格莱德(UTC+01:00)',
             '奥地利 - 维也纳(UTC+01:00)', '安哥拉 - 罗安达(UTC+01:00)', '安道尔 - 安道尔(UTC+01:00)', '尼日利亚 - 拉各斯(UTC+01:00)',
             '尼日尔 - 尼亚美(UTC+01:00)', '德国 - 柏林/布辛根(UTC+01:00)', '意大利 - 罗马(UTC+01:00)', '挪威 - 奥斯陆(UTC+01:00)',
             '捷克 - 布拉格(UTC+01:00)', '摩洛哥 - 卡萨布兰卡(UTC+01:00)', '摩纳哥 - 摩纳哥(UTC+01:00)', '斯洛伐克 - 布拉迪斯拉发(UTC+01:00)',
             '斯洛文尼亚 - 卢布尔雅那(UTC+01:00)', '斯瓦尔巴和扬马延 - 朗伊尔城(UTC+01:00)', '梵蒂冈 - 梵蒂冈(UTC+01:00)', '比利时 - 布鲁塞尔(UTC+01:00)',
             '法国 - 巴黎(UTC+01:00)', '波兰 - 华沙(UTC+01:00)', '波斯尼亚和黑塞哥维那 - 萨拉热窝(UTC+01:00)', '瑞典 - 斯德哥尔摩(UTC+01:00)',
             '瑞士 - 苏黎世(UTC+01:00)', '直布罗陀 - 直布罗陀(UTC+01:00)', '突尼斯 - 突尼斯(UTC+01:00)', '荷兰 - 阿姆斯特丹(UTC+01:00)',
             '西撒哈拉 - 阿尤恩(UTC+01:00)', '西班牙 - 休达/马德里(UTC+01:00)', '贝宁 - 波多诺伏(UTC+01:00)', '赤道几内亚 - 马拉博(UTC+01:00)',
             '阿尔及利亚 - 阿尔及尔(UTC+01:00)', '阿尔巴尼亚 - 地拉那(UTC+01:00)', '马耳他 - 马耳他(UTC+01:00)', '黑山 - 波德戈里察(UTC+01:00)',
             '乌克兰 - 基辅/乌日哥罗德/扎波罗热(UTC+02:00)', '以色列 - 耶路撒冷(UTC+02:00)', '俄罗斯 - 加里宁格勒(UTC+02:00)',
             '保加利亚 - 索非亚(UTC+02:00)', '刚果（金） - 卢本巴希(UTC+02:00)', '利比亚 - 的黎波里(UTC+02:00)', '南苏丹 - 朱巴(UTC+02:00)',
             '南非 - 约翰内斯堡(UTC+02:00)', '博茨瓦纳 - 哈博罗内(UTC+02:00)', '卢旺达 - 基加利(UTC+02:00)', '埃及 - 开罗(UTC+02:00)',
             '塞浦路斯 - 法马古斯塔/尼科西亚(UTC+02:00)', '奥兰群岛 - 玛丽港(UTC+02:00)', '巴勒斯坦 - 加沙/希伯伦(UTC+02:00)',
             '布隆迪 - 布琼布拉(UTC+02:00)', '希腊 - 雅典(UTC+02:00)', '拉脱维亚 - 里加(UTC+02:00)', '摩尔多瓦 - 基希讷乌(UTC+02:00)',
             '斯威士兰 - 姆巴巴纳(UTC+02:00)', '津巴布韦 - 哈拉雷(UTC+02:00)', '爱沙尼亚 - 塔林(UTC+02:00)', '立陶宛 - 维尔纽斯(UTC+02:00)',
             '纳米比亚 - 温得和克(UTC+02:00)', '罗马尼亚 - 布加勒斯特(UTC+02:00)', '芬兰 - 赫尔辛基(UTC+02:00)', '苏丹 - 喀土穆(UTC+02:00)',
             '莫桑比克 - 马普托(UTC+02:00)', '莱索托 - 马塞卢(UTC+02:00)', '赞比亚 - 卢萨卡(UTC+02:00)', '马拉维 - 布兰太尔(UTC+02:00)',
             '黎巴嫩 - 贝鲁特(UTC+02:00)', '乌克兰 - 辛菲罗波尔(UTC+03:00)', '乌干达 - 坎帕拉(UTC+03:00)', '也门 - 亚丁(UTC+03:00)',
             '伊拉克 - 巴格达(UTC+03:00)', '俄罗斯 - 基洛夫/莫斯科(UTC+03:00)', '南极洲 - 昭和(UTC+03:00)', '卡塔尔 - 卡塔尔(UTC+03:00)',
             '厄立特里亚 - 阿斯马拉(UTC+03:00)', '叙利亚 - 大马士革(UTC+03:00)', '吉布提 - 吉布提(UTC+03:00)', '土耳其 - 伊斯坦布尔(UTC+03:00)',
             '坦桑尼亚 - 达累斯萨拉姆(UTC+03:00)', '埃塞俄比亚 - 亚的斯亚贝巴(UTC+03:00)', '巴林 - 巴林(UTC+03:00)', '沙特阿拉伯 - 利雅得(UTC+03:00)',
             '白俄罗斯 - 明斯克(UTC+03:00)', '科威特 - 科威特(UTC+03:00)', '科摩罗 - 科摩罗(UTC+03:00)', '索马里 - 摩加迪沙(UTC+03:00)',
             '约旦 - 安曼(UTC+03:00)', '肯尼亚 - 内罗毕(UTC+03:00)', '马约特 - 马约特(UTC+03:00)', '马达加斯加 - 安塔那那利佛(UTC+03:00)',
             '伊朗 - 德黑兰(UTC+03:30)', '亚美尼亚 - 埃里温(UTC+04:00)', '俄罗斯 - 阿斯特拉罕/萨马拉(UTC+04:00)', '塞舌尔 - 马埃岛(UTC+04:00)',
             '格鲁吉亚 - 第比利斯(UTC+04:00)', '毛里求斯 - 毛里求斯(UTC+04:00)', '留尼汪 - 留尼汪(UTC+04:00)', '阿塞拜疆 - 巴库(UTC+04:00)',
             '阿拉伯联合酋长国 - 迪拜(UTC+04:00)', '阿曼 - 马斯喀特(UTC+04:00)', '阿富汗 - 喀布尔(UTC+04:30)', '乌兹别克斯坦 - 撒马尔罕/塔什干(UTC+05:00)',
             '俄罗斯 - 叶卡捷琳堡(UTC+05:00)', '南极洲 - 莫森(UTC+05:00)', '哈萨克斯坦 - 阿克套/阿克托别(UTC+05:00)', '土库曼斯坦 - 阿什哈巴德(UTC+05:00)',
             '塔吉克斯坦 - 杜尚别(UTC+05:00)', '巴基斯坦 - 卡拉奇(UTC+05:00)', '法属南部领地 - 凯尔盖朗(UTC+05:00)', '马尔代夫 - 马尔代夫(UTC+05:00)',
             '印度 - 加尔各答(UTC+05:30)', '斯里兰卡 - 科伦坡(UTC+05:30)', '尼泊尔 - 加德满都(UTC+05:45)', '不丹 - 廷布(UTC+06:00)',
             '中国 - 乌鲁木齐(UTC+06:00)', '俄罗斯 - 鄂木斯克(UTC+06:00)', '南极洲 - 沃斯托克(UTC+06:00)', '吉尔吉斯斯坦 - 比什凯克(UTC+06:00)',
             '哈萨克斯坦 - 阿拉木图/库斯塔奈(UTC+06:00)', '孟加拉国 - 达卡(UTC+06:00)', '英属印度洋领地 - 查戈斯(UTC+06:00)',
             '科科斯（基林）群岛 - 可可斯(UTC+06:30)', '缅甸 - 仰光(UTC+06:30)', '俄罗斯 - 巴尔瑙尔/克拉斯诺亚尔斯克(UTC+07:00)',
             '南极洲 - 戴维斯(UTC+07:00)', '印度尼西亚 - 雅加达/坤甸(UTC+07:00)', '圣诞岛 - 圣诞岛(UTC+07:00)', '柬埔寨 - 金边(UTC+07:00)',
             '泰国 - 曼谷(UTC+07:00)', '老挝 - 万象(UTC+07:00)', '蒙古 - 科布多(UTC+07:00)', '越南 - 胡志明市(UTC+07:00)']
timezone_mapping = {
    '中国 - 北京(UTC+08:00)': 'Asia/Shanghai',
    '中国 - 台北(UTC+08:00)': 'Asia/Taipei',
    '俄罗斯 - 伊尔库茨克(UTC+08:00)': 'Asia/Irkutsk',
    '印度尼西亚 - 望加锡(UTC+08:00)': 'Asia/Makassar',
    '文莱 - 文莱(UTC+08:00)': 'Asia/Brunei',
    '新加坡 - 新加坡(UTC+08:00)': 'Asia/Singapore',
    '澳大利亚 - 珀斯(UTC+08:00)': 'Australia/Perth',
    '菲律宾 - 马尼拉(UTC+08:00)': 'Asia/Manila',
    '蒙古 - 乔巴山/乌兰巴托(UTC+08:00)': 'Asia/Ulaanbaatar',
    '马来西亚 - 吉隆坡/古晋(UTC+08:00)': 'Asia/Kuala_Lumpur',
    '澳大利亚 - 尤克拉(UTC+08:45)': 'Australia/Eucla',
    '东帝汶 - 帝力(UTC+09:00)': 'Asia/Dili',
    '俄罗斯 - 赤塔/汉德加/雅库茨克(UTC+09:00)': 'Asia/Yakutsk',
    '印度尼西亚 - 查亚普拉(UTC+09:00)': 'Asia/Jayapura',
    '帕劳 - 帕劳(UTC+09:00)': 'Pacific/Palau',
    '日本 - 东京(UTC+09:00)': 'Asia/Tokyo',
    '朝鲜 - 平壤(UTC+09:00)': 'Asia/Pyongyang',
    '韩国 - 首尔(UTC+09:00)': 'Asia/Seoul',
    '澳大利亚 - 达尔文(UTC+09:30)': 'Australia/Darwin',
    '俄罗斯 - 乌斯内拉/符拉迪沃斯托克(UTC+10:00)': 'Asia/Vladivostok',
    '关岛 - 关岛(UTC+10:00)': 'Pacific/Guam',
    '北马里亚纳群岛 - 塞班(UTC+10:00)': 'Pacific/Saipan',
    '南极洲 - 迪蒙·迪维尔(UTC+10:00)': 'Antarctica/DumontDUrville',
    '密克罗尼西亚 - 特鲁克群岛(UTC+10:00)': 'Pacific/Chuuk',
    '巴布亚新几内亚 - 莫尔兹比港(UTC+10:00)': 'Pacific/Port_Moresby',
    '澳大利亚 - 布里斯班/林德曼(UTC+10:00)': 'Australia/Brisbane',
    '澳大利亚 - 阿德莱德/布罗肯希尔(UTC+10:30)': 'Australia/Adelaide',
    '俄罗斯 - 马加丹/萨哈林(UTC+11:00)': 'Asia/Magadan',
    '南极洲 - 卡塞(UTC+11:00)': 'Antarctica/Casey',
    '密克罗尼西亚 - 库赛埃/波纳佩岛(UTC+11:00)': 'Pacific/Pohnpei',
    '巴布亚新几内亚 - 布干维尔(UTC+11:00)': 'Pacific/Bougainville',
    '所罗门群岛 - 瓜达尔卡纳尔(UTC+11:00)': 'Pacific/Guadalcanal',
    '新喀里多尼亚 - 努美阿(UTC+11:00)': 'Pacific/Noumea',
    '澳大利亚 - 麦格理/悉尼(UTC+11:00)': 'Australia/Sydney',
    '瓦努阿图 - 埃法特(UTC+11:00)': 'Pacific/Efate',
    '俄罗斯 - 阿纳德尔/堪察加(UTC+12:00)': 'Asia/Anadyr',
    '图瓦卢 - 富纳富提(UTC+12:00)': 'Pacific/Funafuti',
    '基里巴斯 - 塔拉瓦(UTC+12:00)': 'Pacific/Tarawa',
    '斐济 - 斐济(UTC+12:00)': 'Pacific/Fiji',
    '瑙鲁 - 瑙鲁(UTC+12:00)': 'Pacific/Nauru',
    '瓦利斯和富图纳 - 瓦利斯(UTC+12:00)': 'Pacific/Wallis',
    '美国本土外小岛屿 - 威克(UTC+12:00)': 'Pacific/Wake',
    '诺福克岛 - 诺福克(UTC+12:00)': 'Pacific/Norfolk',
    '马绍尔群岛 - 夸贾林/马朱罗(UTC+12:00)': 'Pacific/Majuro',
    '南极洲 - 麦克默多/奥克兰(UTC+13:00)': 'Pacific/Auckland',
    '基里巴斯 - 恩德伯里(UTC+13:00)': 'Pacific/Enderbury',
    '托克劳 - 法考福(UTC+13:00)': 'Pacific/Fakaofo',
    '新西兰 - 奥克兰(UTC+13:00)': 'Pacific/Auckland',
    '汤加 - 东加塔布(UTC+13:00)': 'Pacific/Tongatapu',
    '萨摩亚 - 阿皮亚(UTC+13:00)': 'Pacific/Apia',
    '新西兰 - 查塔姆(UTC+13:45)': 'Pacific/Chatham',
    '基里巴斯 - 基里地马地岛(UTC+14:00)': 'Pacific/Kiritimati',
    '纽埃 - 纽埃(UTC-11:00)': 'Pacific/Niue',
    '美国本土外小岛屿 - 中途岛(UTC-11:00)': 'Pacific/Midway',
    '美属萨摩亚 - 帕果帕果(UTC-11:00)': 'Pacific/Pago_Pago',
    '库克群岛 - 拉罗汤加(UTC-10:00)': 'Pacific/Rarotonga',
    '法属波利尼西亚 - 塔希提(UTC-10:00)': 'Pacific/Tahiti',
    '美国 - 埃达克/檀香山(UTC-10:00)': 'Pacific/Honolulu',
    '美国本土外小岛屿 - 约翰斯顿(UTC-10:00)': 'Pacific/Johnston',
    '法属波利尼西亚 - 马克萨斯(UTC-09:30)': 'Pacific/Marquesas',
    '法属波利尼西亚 - 甘比尔(UTC-09:00)': 'Pacific/Gambier',
    '美国 - 安克雷奇/朱诺(UTC-09:00)': 'America/Anchorage',
    '加拿大 - 温哥华(UTC-08:00)': 'America/Vancouver',
    '墨西哥 - 蒂华纳/圣伊萨贝尔(UTC-08:00)': 'America/Tijuana',
    '皮特凯恩群岛 - 皮特凯恩(UTC-08:00)': 'Pacific/Pitcairn',
    '美国 - 洛杉矶(UTC-08:00)': 'America/Los_Angeles',
    '加拿大 - 剑桥湾/克雷斯顿(UTC-07:00)': 'America/Cambridge_Bay',
    '墨西哥 - 华雷斯城/埃莫西约(UTC-07:00)': 'America/Hermosillo',
    '美国 - 博伊西/丹佛(UTC-07:00)': 'America/Denver',
    '伯利兹 - 伯利兹(UTC-06:00)': 'America/Belize',
    '加拿大 - 雷尼河/兰今湾(UTC-06:00)': 'America/Rankin_Inlet',
    '危地马拉 - 危地马拉(UTC-06:00)': 'America/Guatemala',
    '厄瓜多尔 - 加拉帕戈斯(UTC-06:00)': 'Pacific/Galapagos',
    '哥斯达黎加 - 哥斯达黎加(UTC-06:00)': 'America/Costa_Rica',
    '墨西哥 - 巴伊亚班德拉斯/奇瓦瓦(UTC-06:00)': 'America/Chihuahua',
    '尼加拉瓜 - 马那瓜(UTC-06:00)': 'America/Managua',
    '洪都拉斯 - 特古西加尔巴(UTC-06:00)': 'America/Tegucigalpa',
    '美国 - 芝加哥/印第安纳州诺克斯(UTC-06:00)': 'America/Chicago',
    '萨尔瓦多 - 萨尔瓦多(UTC-06:00)': 'America/El_Salvador',
    '加拿大 - 阿蒂科肯/伊魁特(UTC-05:00)': 'America/Iqaluit',
    '厄瓜多尔 - 瓜亚基尔(UTC-05:00)': 'America/Guayaquil',
    '古巴 - 哈瓦那(UTC-05:00)': 'America/Havana',
    '哥伦比亚 - 波哥大(UTC-05:00)': 'America/Bogota',
    '墨西哥 - 坎昆(UTC-05:00)': 'America/Cancun',
    '巴哈马 - 拿骚(UTC-05:00)': 'America/Nassau',
    '巴拿马 - 巴拿马(UTC-05:00)': 'America/Panama',
    '巴西 - 依伦尼贝/里奥布郎库(UTC-05:00)': 'America/Rio_Branco',
    '开曼群岛 - 开曼(UTC-05:00)': 'America/Cayman',
    '智利 - 复活节岛(UTC-05:00)': 'Pacific/Easter',
    '海地 - 太子港(UTC-05:00)': 'America/Port-au-Prince',
    '牙买加 - 牙买加(UTC-05:00)': 'America/Jamaica',
    '特克斯和凯科斯群岛 - 大特克(UTC-05:00)': 'America/Grand_Turk',
    '秘鲁 - 利马(UTC-05:00)': 'America/Lima',
    '美国 - 底特律/印第安纳波利斯(UTC-05:00)': 'America/Detroit',
    '加拿大 - 布兰克萨布隆/格莱斯贝(UTC-04:00)': 'America/Goose_Bay',
    '圣卢西亚 - 圣卢西亚(UTC-04:00)': 'America/St_Lucia',
    '圣基茨和尼维斯 - 圣基茨(UTC-04:00)': 'America/St_Kitts',
    '圣巴泰勒米 - 圣巴泰勒米岛(UTC-04:00)': 'America/St_Barthelemy',
    '圣文森特和格林纳丁斯 - 圣文森特(UTC-04:00)': 'America/St_Vincent',
    '圭亚那 - 圭亚那(UTC-04:00)': 'America/Guyana',
    '多米尼克 - 多米尼加(UTC-04:00)': 'America/Dominica',
    '多米尼加共和国 - 圣多明各(UTC-04:00)': 'America/Santo_Domingo',
    '委内瑞拉 - 加拉加斯(UTC-04:00)': 'America/Caracas',
    '安圭拉 - 安圭拉(UTC-04:00)': 'America/Anguilla',
    '安提瓜和巴布达 - 安提瓜(UTC-04:00)': 'America/Antigua',
    '巴巴多斯 - 巴巴多斯(UTC-04:00)': 'America/Barbados',
    '巴西 - 博阿维斯塔/大坎普(UTC-04:00)': 'America/Campo_Grande',
    '库拉索 - 库拉索(UTC-04:00)': 'America/Curacao',
    '格林纳达 - 格林纳达(UTC-04:00)': 'America/Grenada',
    '格陵兰 - 图勒(UTC-04:00)': 'America/Thule',
    '法属圣马丁 - 马里戈特(UTC-04:00)': 'America/Marigot',
    '波多黎各 - 波多黎各(UTC-04:00)': 'America/Puerto_Rico',
    '特立尼达和多巴哥 - 西班牙港(UTC-04:00)': 'America/Port_of_Spain',
    '玻利维亚 - 拉巴斯(UTC-04:00)': 'America/La_Paz',
    '瓜德罗普 - 瓜德罗普(UTC-04:00)': 'America/Guadeloupe',
    '百慕大 - 百慕大(UTC-04:00)': 'Atlantic/Bermuda',
    '美属维尔京群岛 - 圣托马斯(UTC-04:00)': 'America/St_Thomas',
    '英属维尔京群岛 - 托尔托拉(UTC-04:00)': 'America/Tortola',
    '荷属加勒比区 - 克拉伦代克(UTC-04:00)': 'America/Kralendijk',
    '荷属圣马丁 - 下太子区(UTC-04:00)': 'America/Lower_Princes',
    '蒙特塞拉特 - 蒙特塞拉特(UTC-04:00)': 'America/Montserrat',
    '阿鲁巴 - 阿鲁巴(UTC-04:00)': 'America/Aruba',
    '马提尼克 - 马提尼克(UTC-04:00)': 'America/Martinique',
    '加拿大 - 圣约翰斯(UTC-03:30)': 'America/St_Johns',
    '乌拉圭 - 蒙得维的亚(UTC-03:00)': 'America/Montevideo',
    '南极洲 - 帕尔默/罗瑟拉(UTC-03:00)': 'Antarctica/Palmer',
    '圣皮埃尔和密克隆群岛 - 密克隆(UTC-03:00)': 'America/Miquelon',
    '巴拉圭 - 亚松森(UTC-03:00)': 'America/Asuncion',
    '巴西 - 阿拉瓜伊纳/巴伊亚(UTC-03:00)': 'America/Bahia',
    '智利 - 蓬塔阿雷纳斯/圣地亚哥(UTC-03:00)': 'America/Santiago',
    '法属圭亚那 - 卡宴(UTC-03:00)': 'America/Cayenne',
    '福克兰群岛（马尔维纳斯群岛） - 斯坦利(UTC-03:00)': 'Atlantic/Stanley',
    '苏里南 - 帕拉马里博(UTC-03:00)': 'America/Paramaribo',
    '阿根廷 - 布宜诺斯艾利斯/卡塔马卡(UTC-03:00)': 'America/Argentina/Buenos_Aires',
    '南乔治亚和南桑威奇群岛 - 南乔治亚(UTC-02:00)': 'Atlantic/South_Georgia',
    '巴西 - 洛罗尼亚(UTC-02:00)': 'America/Noronha',
    '格陵兰 - 努克(UTC-02:00)': 'America/Nuuk',
    '佛得角 - 佛得角(UTC-01:00)': 'Atlantic/Cape_Verde',
    # 影駅后的地区，UTC+00:00及以东
    '格陵兰 - 斯科列斯比桑德(UTC-01:00)': 'America/Scoresbysund',
    '葡萄牙 - 亚速尔群岛(UTC-01:00)': 'Atlantic/Azores',
    '冈比亚 - 班珠尔(UTC+00:00)': 'Africa/Banjul',
    '冰岛 - 雷克雅未克(UTC+00:00)': 'Atlantic/Reykjavik',
    '几内亚 - 科纳克里(UTC+00:00)': 'Africa/Conakry',
    '几内亚比绍 - 比绍(UTC+00:00)': 'Africa/Bissau',
    '利比里亚 - 蒙罗维亚(UTC+00:00)': 'Africa/Monrovia',
    '加纳 - 阿克拉(UTC+00:00)': 'Africa/Accra',
    '南极洲 - 特罗尔(UTC+00:00)': 'Antarctica/Troll',
    '圣多美和普林西比 - 圣多美(UTC+00:00)': 'Africa/Sao_Tome',
    '圣赫勒拿 - 圣赫勒拿(UTC+00:00)': 'Atlantic/St_Helena',
    '塞内加尔 - 达喀尔(UTC+00:00)': 'Africa/Dakar',
    '塞拉利昂 - 弗里敦(UTC+00:00)': 'Africa/Freetown',
    '多哥 - 洛美(UTC+00:00)': 'Africa/Lome',
    '布基纳法索 - 瓦加杜古(UTC+00:00)': 'Africa/Ouagadougou',
    '根西岛 - 根西岛(UTC+00:00)': 'Europe/Guernsey',
    '格陵兰 - 丹马沙文(UTC+00:00)': 'America/Danmarkshavn',
    '毛里塔尼亚 - 努瓦克肖特(UTC+00:00)': 'Africa/Nouakchott',
    '法罗群岛 - 法罗(UTC+00:00)': 'Atlantic/Faroe',
    '泽西岛 - 泽西岛(UTC+00:00)': 'Europe/Jersey',
    '爱尔兰 - 都柏林(UTC+00:00)': 'Europe/Dublin',
    '科特迪瓦 - 阿比让/雷克雅未克(UTC+00:00)': 'Africa/Abidjan',
    '英国 - 伦敦(UTC+00:00)': 'Europe/London',
    '葡萄牙 - 马德拉/里斯本(UTC+00:00)': 'Europe/Lisbon',
    '西班牙 - 加那利(UTC+00:00)': 'Atlantic/Canary',
    '马恩岛 - 马恩岛(UTC+00:00)': 'Europe/Isle_of_Man',
    '马里 - 巴马科(UTC+00:00)': 'Africa/Bamako',
    '中非共和国 - 班吉(UTC+01:00)': 'Africa/Bangui',
    '丹麦 - 哥本哈根(UTC+01:00)': 'Europe/Copenhagen',
    '乍得 - 恩贾梅纳(UTC+01:00)': 'Africa/Ndjamena',
    '克罗地亚 - 萨格勒布(UTC+01:00)': 'Europe/Zagreb',
    '列支敦士登 - 瓦杜兹(UTC+01:00)': 'Europe/Vaduz',
    '刚果（布） - 布拉柴维尔(UTC+01:00)': 'Africa/Brazzaville',
    '刚果（金） - 金沙萨(UTC+01:00)': 'Africa/Kinshasa',
    '加蓬 - 利伯维尔(UTC+01:00)': 'Africa/Libreville',
    '匈牙利 - 布达佩斯(UTC+01:00)': 'Europe/Budapest',
    '北马其顿 - 斯科普里(UTC+01:00)': 'Europe/Skopje',
    '卢森堡 - 卢森堡(UTC+01:00)': 'Europe/Luxembourg',
    '喀麦隆 - 杜阿拉(UTC+01:00)': 'Africa/Douala',
    '圣马力诺 - 圣马力诺(UTC+01:00)': 'Europe/San_Marino',
    '塞尔维亚 - 贝尔格莱德(UTC+01:00)': 'Europe/Belgrade',
    '奥地利 - 维也纳(UTC+01:00)': 'Europe/Vienna',
    '安哥拉 - 罗安达(UTC+01:00)': 'Africa/Luanda',
    '安道尔 - 安道尔(UTC+01:00)': 'Europe/Andorra',
    '尼日利亚 - 拉各斯(UTC+01:00)': 'Africa/Lagos',
    '尼日尔 - 尼亚美(UTC+01:00)': 'Africa/Niamey',
    '德国 - 柏林/布辛根(UTC+01:00)': 'Europe/Berlin',
    '意大利 - 罗马(UTC+01:00)': 'Europe/Rome',
    '挪威 - 奥斯陆(UTC+01:00)': 'Europe/Oslo',
    '捷克 - 布拉格(UTC+01:00)': 'Europe/Prague',
    '摩洛哥 - 卡萨布兰卡(UTC+01:00)': 'Africa/Casablanca',
    '摩纳哥 - 摩纳哥(UTC+01:00)': 'Europe/Monaco',
    '斯洛伐克 - 布拉迪斯拉发(UTC+01:00)': 'Europe/Bratislava',
    '斯洛文尼亚 - 卢布尔雅那(UTC+01:00)': 'Europe/Ljubljana',
    '斯瓦尔巴和扬马延 - 朗伊尔城(UTC+01:00)': 'Arctic/Longyearbyen',
    '梵蒂冈 - 梵蒂冈(UTC+01:00)': 'Europe/Vatican',
    '比利时 - 布鲁塞尔(UTC+01:00)': 'Europe/Brussels',
    '法国 - 巴黎(UTC+01:00)': 'Europe/Paris',
    '波兰 - 华沙(UTC+01:00)': 'Europe/Warsaw',
    '波斯尼亚和黑塞哥维那 - 萨拉热窝(UTC+01:00)': 'Europe/Sarajevo',
    '瑞典 - 斯德哥尔摩(UTC+01:00)': 'Europe/Stockholm',
    '瑞士 - 苏黎世(UTC+01:00)': 'Europe/Zurich',
    '直布罗陀 - 直布罗陀(UTC+01:00)': 'Europe/Gibraltar',
    '突尼斯 - 突尼斯(UTC+01:00)': 'Africa/Tunis',
    '荷兰 - 阿姆斯特丹(UTC+01:00)': 'Europe/Amsterdam',
    '西撒哈拉 - 阿尤恩(UTC+01:00)': 'Africa/El_Aaiun',
    '西班牙 - 休达/马德里(UTC+01:00)': 'Europe/Madrid',
    '贝宁 - 波多诺伏(UTC+01:00)': 'Africa/Porto-Novo',
    '赤道几内亚 - 马拉博(UTC+01:00)': 'Africa/Malabo',
    '阿尔及利亚 - 阿尔及尔(UTC+01:00)': 'Africa/Algiers',
    '阿尔巴尼亚 - 地拉那(UTC+01:00)': 'Europe/Tirane',
    '马耳他 - 马耳他(UTC+01:00)': 'Europe/Malta',
    '黑山 - 波德戈里察(UTC+01:00)': 'Europe/Podgorica',
    '乌克兰 - 基辅/乌日哥罗德/扎波罗热(UTC+02:00)': 'Europe/Kiev',
    '以色列 - 耶路撒冷(UTC+02:00)': 'Asia/Jerusalem',
    '俄罗斯 - 加里宁格勒(UTC+02:00)': 'Europe/Kaliningrad',
    '保加利亚 - 索非亚(UTC+02:00)': 'Europe/Sofia',
    '刚果（金） - 卢本巴希(UTC+02:00)': 'Africa/Lubumbashi',
    '利比亚 - 的黎波里(UTC+02:00)': 'Africa/Tripoli',
    '南苏丹 - 朱巴(UTC+02:00)': 'Africa/Juba',
    '南非 - 约翰内斯堡(UTC+02:00)': 'Africa/Johannesburg',
    '博茨瓦纳 - 哈博罗内(UTC+02:00)': 'Africa/Gaborone',
    '卢旺达 - 基加利(UTC+02:00)': 'Africa/Kigali',
    '埃及 - 开罗(UTC+02:00)': 'Africa/Cairo',
    '塞浦路斯 - 法马古斯塔/尼科西亚(UTC+02:00)': 'Asia/Nicosia',
    '奥兰群岛 - 玛丽港(UTC+02:00)': 'Europe/Mariehamn',
    '巴勒斯坦 - 加沙/希伯伦(UTC+02:00)': 'Asia/Gaza',
    '布隆迪 - 布琼布拉(UTC+02:00)': 'Africa/Bujumbura',
    '希腊 - 雅典(UTC+02:00)': 'Europe/Athens',
    '拉脱维亚 - 里加(UTC+02:00)': 'Europe/Riga',
    '摩尔多瓦 - 基希讷乌(UTC+02:00)': 'Europe/Chisinau',
    '斯威士兰 - 姆巴巴纳(UTC+02:00)': 'Africa/Mbabane',
    '津巴布韦 - 哈拉雷(UTC+02:00)': 'Africa/Harare',
    '爱沙尼亚 - 塔林(UTC+02:00)': 'Europe/Tallinn',
    '立陶宛 - 维尔纽斯(UTC+02:00)': 'Europe/Vilnius',
    '纳米比亚 - 温得和克(UTC+02:00)': 'Africa/Windhoek',
    '罗马尼亚 - 布加勒斯特(UTC+02:00)': 'Europe/Bucharest',
    '芬兰 - 赫尔辛基(UTC+02:00)': 'Europe/Helsinki',
    '苏丹 - 喀土穆(UTC+02:00)': 'Africa/Khartoum',
    '莫桑比克 - 马普托(UTC+02:00)': 'Africa/Maputo',
    '莱索托 - 马塞卢(UTC+02:00)': 'Africa/Maseru',
    '赞比亚 - 卢萨卡(UTC+02:00)': 'Africa/Lusaka',
    '马拉维 - 布兰太尔(UTC+02:00)': 'Africa/Blantyre',
    '黎巴嫩 - 贝鲁特(UTC+02:00)': 'Asia/Beirut',
    '乌克兰 - 辛菲罗波尔(UTC+03:00)': 'Europe/Simferopol',
    '乌干达 - 坎帕拉(UTC+03:00)': 'Africa/Kampala',
    '也门 - 亚丁(UTC+03:00)': 'Asia/Aden',
    '伊拉克 - 巴格达(UTC+03:00)': 'Asia/Baghdad',
    '俄罗斯 - 基洛夫/莫斯科(UTC+03:00)': 'Europe/Moscow',
    '南极洲 - 昭和(UTC+03:00)': 'Antarctica/Syowa',
    '卡塔尔 - 卡塔尔(UTC+03:00)': 'Asia/Qatar',
    '厄立特里亚 - 阿斯马拉(UTC+03:00)': 'Africa/Asmara',
    '叙利亚 - 大马士革(UTC+03:00)': 'Asia/Damascus',
    '吉布提 - 吉布提(UTC+03:00)': 'Africa/Djibouti',
    '土耳其 - 伊斯坦布尔(UTC+03:00)': 'Europe/Istanbul',
    '坦桑尼亚 - 达累斯萨拉姆(UTC+03:00)': 'Africa/Dar_es_Salaam',
    '埃塞俄比亚 - 亚的斯亚贝巴(UTC+03:00)': 'Africa/Addis_Ababa',
    '巴林 - 巴林(UTC+03:00)': 'Asia/Bahrain',
    '沙特阿拉伯 - 利雅得(UTC+03:00)': 'Asia/Riyadh',
    '白俄罗斯 - 明斯克(UTC+03:00)': 'Europe/Minsk',
    '科威特 - 科威特(UTC+03:00)': 'Asia/Kuwait',
    '科摩罗 - 科摩罗(UTC+03:00)': 'Indian/Comoro',
    '索马里 - 摩加迪沙(UTC+03:00)': 'Africa/Mogadishu',
    '约旦 - 安曼(UTC+03:00)': 'Asia/Amman',
    '肯尼亚 - 内罗毕(UTC+03:00)': 'Africa/Nairobi',
    '马约特 - 马约特(UTC+03:00)': 'Indian/Mayotte',
    '马达加斯加 - 安塔那那利佛(UTC+03:00)': 'Indian/Antananarivo',
    '伊朗 - 德黑兰(UTC+03:30)': 'Asia/Tehran',
    '亚美尼亚 - 埃里温(UTC+04:00)': 'Asia/Yerevan',
    '俄罗斯 - 阿斯特拉罕/萨马拉(UTC+04:00)': 'Europe/Samara',
    '塞舌尔 - 马埃岛(UTC+04:00)': 'Indian/Mahe',
    '格鲁吉亚 - 第比利斯(UTC+04:00)': 'Asia/Tbilisi',
    '毛里求斯 - 毛里求斯(UTC+04:00)': 'Indian/Mauritius',
    '留尼汪 - 留尼汪(UTC+04:00)': 'Indian/Reunion',
    '阿塞拜疆 - 巴库(UTC+04:00)': 'Asia/Baku',
    '阿拉伯联合酋长国 - 迪拜(UTC+04:00)': 'Asia/Dubai',
    '阿曼 - 马斯喀特(UTC+04:00)': 'Asia/Muscat',
    '阿富汗 - 喀布尔(UTC+04:30)': 'Asia/Kabul',
    '乌兹别克斯坦 - 撒马尔罕/塔什干(UTC+05:00)': 'Asia/Tashkent',
    '俄罗斯 - 叶卡捷琳堡(UTC+05:00)': 'Asia/Yekaterinburg',
    '南极洲 - 莫森(UTC+05:00)': 'Antarctica/Mawson',
    '哈萨克斯坦 - 阿克套/阿克托别(UTC+05:00)': 'Asia/Aqtobe',
    '土库曼斯坦 - 阿什哈巴德(UTC+05:00)': 'Asia/Ashgabat',
    '塔吉克斯坦 - 杜尚别(UTC+05:00)': 'Asia/Dushanbe',
    '巴基斯坦 - 卡拉奇(UTC+05:00)': 'Asia/Karachi',
    '法属南部领地 - 凯尔盖朗(UTC+05:00)': 'Indian/Kerguelen',
    '马尔代夫 - 马尔代夫(UTC+05:00)': 'Indian/Maldives',
    '印度 - 加尔各答(UTC+05:30)': 'Asia/Kolkata',
    '斯里兰卡 - 科伦坡(UTC+05:30)': 'Asia/Colombo',
    '尼泊尔 - 加德满都(UTC+05:45)': 'Asia/Kathmandu',
    '不丹 - 廷布(UTC+06:00)': 'Asia/Thimphu',
    '中国 - 乌鲁木齐(UTC+06:00)': 'Asia/Urumqi',
    '俄罗斯 - 鄂木斯克(UTC+06:00)': 'Asia/Omsk',
    '南极洲 - 沃斯托克(UTC+06:00)': 'Antarctica/Vostok',
    '吉尔吉斯斯坦 - 比什凯克(UTC+06:00)': 'Asia/Bishkek',
    '哈萨克斯坦 - 阿拉木图/库斯塔奈(UTC+06:00)': 'Asia/Almaty',
    '孟加拉国 - 达卡(UTC+06:00)': 'Asia/Dhaka',
    '英属印度洋领地 - 查戈斯(UTC+06:00)': 'Indian/Chagos',
    '科科斯（基林）群岛 - 可可斯(UTC+06:30)': 'Indian/Cocos',
    '缅甸 - 仰光(UTC+06:30)': 'Asia/Yangon',
    '俄罗斯 - 巴尔瑙尔/克拉斯诺亚尔斯克(UTC+07:00)': 'Asia/Krasnoyarsk',
    '南极洲 - 戴维斯(UTC+07:00)': 'Antarctica/Davis',
    '印度尼西亚 - 雅加达/坤甸(UTC+07:00)': 'Asia/Jakarta',
    '圣诞岛 - 圣诞岛(UTC+07:00)': 'Indian/Christmas',
    '柬埔寨 - 金边(UTC+07:00)': 'Asia/Phnom_Penh',
    '泰国 - 曼谷(UTC+07:00)': 'Asia/Bangkok',
    '老挝 - 万象(UTC+07:00)': 'Asia/Vientiane',
    '蒙古 - 科布多(UTC+07:00)': 'Asia/Hovd',
    '越南 - 胡志明市(UTC+07:00)': 'Asia/Ho_Chi_Minh'
}
datetime_format = "%Y年%m月%d日 %H:%M"
ip = '192.168.1.100'


def setup_logger():
    # 第一步，创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级开关
    current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
    # 创建文件输出处理器
    log_dir = os.path.join(current_working_dir, "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, '{}.log'.format(time.strftime("%Y%m%d_%H%M%S", time.localtime())))
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 第三步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)

    # 第四步，将handler添加到logger里面
    logger.addHandler(file_handler)

    # 如果需要同时需要在终端上输出，定于一個streamHandler
    print_handler = logging.StreamHandler()  # 往屏幕上输出
    print_handler.setFormatter(formatter)  # 设置屏幕上显示的格式
    logger.addHandler(print_handler)

    return logger


logger = setup_logger()
# 连接到设备
subprocess.Popen(f'adb connect {ip}')
d = u2.connect(ip)

d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
time.sleep(5)
d(text="时间与日期").click()
i = 0
while i < len(time_zone):
    try:
        d(resourceId="com.h3c.settings:id/tv_timezone").click()
        while True:
            if d(text=time_zone[i]).exists():
                while d(resourceId="com.h3c.settings:id/btn_close").exists() is True:
                    d(text=time_zone[i]).click()
                break
            else:
                list_view = d(resourceId="com.h3c.settings:id/rv_list")
                # 获取控件的尺寸和位置
                bounds = list_view.info["bounds"]
                middle_x = (bounds["left"] + bounds["right"]) // 2
                start_y = bounds["top"] + 200
                # 滑动的距离
                end_y = start_y - 500

                # 使用 gesture 进行滑动
                d.swipe(middle_x, start_y, middle_x, end_y, 0.1)
        day_now = d(resourceId="com.h3c.settings:id/tv_date").get_text()
        time_now = d(resourceId="com.h3c.settings:id/tv_time").get_text()
        # 组合日期和时间并解析
        datetime_str = f"{day_now} {time_now}"
        naive_target_datetime = datetime.strptime(datetime_str, datetime_format)
        # 获取当前的北京时间
        current_timezone = pytz.timezone(timezone_mapping[time_zone[i]])
        # 当前大屏时间，转换格式
        target_datetime = current_timezone.localize(naive_target_datetime)
        # 当前所选择时区的实际时间
        current_time = datetime.now(current_timezone)

        time_difference = abs(current_time - target_datetime)
        # 判断时间差是否在2分钟内
        is_within_two_minutes = time_difference <= timedelta(minutes=2)
        if is_within_two_minutes is True:
            logger.info(f"{time_zone[i]}时区验证通过\n")
        else:
            logger.info(f"========两个时区不相等:{is_within_two_minutes}========")
            logger.info(f"时区选择为:{time_zone[i]}")
            logger.info(f"时区时间为:{current_time}")
            logger.info(f"大屏时间为:{target_datetime}\n")
        i += 1
    except Exception as e:
        logger.info(f"{time_zone[i]}时区验证时失败，失败原因为{e}，重新执行\n")
        subprocess.Popen(f'adb disconnect {ip}')
        time.sleep(10)
        subprocess.Popen(f'adb connect {ip}')
        d = u2.connect(ip)
        time.sleep(5)
        d.app_stop_all()
        logger.info("已关闭所有应用")
        d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
        time.sleep(5)
        d(text="时间与日期").click()
