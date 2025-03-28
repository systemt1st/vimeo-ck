# Vimeo账号Cookie提取工具

这是一个自动化提取Vimeo账号Cookie的工具，并通过拨号连接动态切换 IP 地址。

## 功能
- 自动在 Vimeo 上创建账号（包括邮箱、姓名、密码）。
- 提取并保存 Vimeo 的 Cookie 到 `cookies.txt` 文件。
- 将账号凭证（邮箱、姓名、密码）记录到 `zhanghao.txt` 文件。
- 通过拨号（RAS）连接动态切换 IP 地址。
- 多线程执行，支持并行处理多个账号。

## 环境要求
- Python 3.x
- [Playwright](https://playwright.dev/)
- `rasdial` 命令（仅限 Windows 系统，用于拨号连接）

### 安装依赖：
```bash
pip install playwright
python -m playwright install
```

## 使用方法
配置拨号连接凭证：
确保在 get_credentials 函数中填写正确的拨号连接信息。

## 处理流程：
脚本会根据设置的拨号频率自动切换 IP 地址。
通过多线程并行处理多个账号的创建。
创建成功后，账号的 Cookie 将保存到 cookies.txt 文件中，账号凭证（邮箱、姓名、密码）将记录到 zhanghao.txt 文件中。

## 注意事项
本工具假设您使用的是 Windows 系统并且已经配置了拨号上网（使用 rasdial）。

请负责任地使用此工具，并确保遵守 Vimeo 的使用条款。
