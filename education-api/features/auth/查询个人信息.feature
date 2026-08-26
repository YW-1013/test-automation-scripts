@auth @myinfo
Feature: 查询个人信息


  Scenario: 查询个人信息_正确的token
    When 用户 admin 查询个人信息
    Then 查询个人信息 操作成功
    And admin 个人信息数据正确
