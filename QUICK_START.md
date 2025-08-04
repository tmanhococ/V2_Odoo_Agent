# 🚀 AI Odoo Agent - Quick Start Guide

## 📋 Yêu cầu hệ thống

- Python 3.8+
- Odoo 17
- Anthropic API Key (tùy chọn)

## ⚡ Khởi động nhanh

### Bước 1: Cài đặt Dependencies

```bash
cd odoo17/addons/ai_odoo_agent
python install_dependencies.py
```

Hoặc cài đặt thủ công:
```bash
pip install -r requirements.txt
```

### Bước 1.5: Test hệ thống (Tùy chọn)

```bash
python test_system.py
```

### Bước 2: Khởi động hệ thống

#### Trên Windows:
```bash
# Double-click file này hoặc chạy trong Command Prompt
start_system.bat
```

#### Trên Linux/Mac:
```bash
# Chạy trong terminal
./start_system.sh
```

#### Hoặc chạy trực tiếp Python:
```bash
# Phiên bản có emoji (Linux/Mac)
python start_system.py

# Phiên bản không có emoji (Windows)
python start_system_no_emoji.py
```

### Bước 3: Truy cập hệ thống

1. **Mở trình duyệt**: http://localhost:8069
2. **Đăng nhập Odoo** (tạo database mới nếu cần)
3. **Cài đặt module**: Apps > Update Apps List > Tìm "AI Odoo Agent" > Install
4. **Sử dụng AI Assistant**: Menu > AI Assistant > Chat with AI

## 🔧 Cấu hình API Key (Tùy chọn)

### Cách 1: Environment Variable
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Cách 2: Trong Odoo Settings
1. Vào Settings > Technical > Parameters
2. Tạo parameter: `ai_agent.anthropic_api_key`
3. Giá trị: `your-api-key-here`

## 📊 Trạng thái hệ thống

Khi khởi động thành công, bạn sẽ thấy:

```
============================================================
🎉 AI Odoo Agent System Started Successfully!
============================================================
📊 System Status:
   ✅ MCP Server: Running on stdio transport
   ✅ Odoo Server: Running on http://localhost:8069

🌐 Access Information:
   📱 Odoo Web Interface: http://localhost:8069
   🤖 AI Assistant: Available in Odoo menu
   📝 MCP Server: Running in background
```

## 🛑 Dừng hệ thống

Nhấn **Ctrl+C** để dừng tất cả services một cách an toàn.

## 🔍 Troubleshooting

### Lỗi thường gặp:

1. **Port 8069 đã được sử dụng**
   - Dừng Odoo instance khác đang chạy
   - Hoặc thay đổi port trong odoo.conf

2. **Module không hiển thị trong Apps**
   - Kiểm tra đường dẫn addons trong odoo.conf
   - Restart Odoo server

3. **MCP Server không khởi động**
   - Kiểm tra Python dependencies: `pip list | grep mcp`
   - Reinstall: `pip install mcp --upgrade`

4. **API Key không hoạt động**
   - Kiểm tra API key có hợp lệ không
   - Thử test với curl: `curl -H "x-api-key: YOUR_KEY" https://api.anthropic.com/v1/messages`

## 📁 Cấu trúc file

```
ai_odoo_agent/
├── start_system.py          # Main launcher
├── start_system.bat         # Windows launcher
├── start_system.sh          # Linux/Mac launcher
├── install_dependencies.py  # Dependency installer
├── test_system.py           # System tester
├── mcp_server/
│   └── odoo_mcp_server.py  # MCP Server
├── models/
│   └── ai_agent_models.py  # Odoo models
├── views/
│   └── ai_agent_views.xml  # UI views
├── requirements.txt         # Dependencies
└── ai_agent_system.log     # System logs
```

## 🎯 Tính năng chính

- 🤖 **AI Assistant**: Chat với Claude AI
- 🔍 **Search Tools**: Tìm kiếm leads, customers
- ➕ **Creation Tools**: Tạo leads, customers mới
- 📊 **Analytics**: Báo cáo doanh số
- 🛡️ **Security**: User approval cho data changes

## 💡 Sử dụng AI Assistant

### Ví dụ lệnh:

```
"Tìm kiếm leads có tên John"
"Hiển thị top 5 khách hàng"
"Tạo lead mới cho Acme Corp"
"Báo cáo doanh số tháng này"
```

## 🔄 Cập nhật hệ thống

```bash
# Pull latest changes
git pull

# Reinstall dependencies
pip install -r requirements.txt --upgrade



## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trong terminal
2. Restart hệ thống
3. Kiểm tra Python version: `python --version`
4. Kiểm tra Odoo version: `python odoo-bin --version`

---

**🎉 Chúc bạn sử dụng AI Odoo Agent thành công!** 