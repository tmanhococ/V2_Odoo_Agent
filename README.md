# AI Odoo Agent (MCP Integration)

AI Agent tích hợp với Odoo 17 sử dụng Model Context Protocol (MCP) và Fast-Agent.

## Tính năng

- 🤖 AI Assistant tích hợp với Odoo ERP
- 🔍 Tìm kiếm và quản lý khách hàng, leads
- 📊 Báo cáo và phân tích bán hàng
- 🛡️ Xác nhận người dùng cho các thao tác thay đổi dữ liệu
- 🔧 Cấu hình linh hoạt

## Cài đặt

### 1. Cài đặt Dependencies

```bash
pip install mcp fast-agent-mcp httpx
```

### 2. Cấu hình API Key

Thiết lập Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Hoặc cấu hình trong Odoo:
- Vào Settings > Technical > Parameters
- Thêm parameter: `ai_agent.anthropic_api_key` với giá trị API key

### 3. Cài đặt Module

1. Copy module vào thư mục `addons`
2. Cập nhật danh sách apps trong Odoo
3. Cài đặt module "AI Odoo Agent"

## Sử dụng

### Khởi động MCP Server

Module sẽ tự động khởi động MCP server khi được cài đặt. Server chạy trên `http://127.0.0.1:8000`.

### Sử dụng AI Assistant

1. Vào menu **AI Assistant > Chat with AI**
2. Nhập câu hỏi hoặc lệnh
3. Nhấn **Send** để gửi
4. AI sẽ trả lời và có thể thực hiện các thao tác

### Các lệnh mẫu

- "Tìm kiếm leads có tên John"
- "Hiển thị top 5 khách hàng"
- "Tạo lead mới cho Acme Corp"
- "Báo cáo doanh số tháng này"

## Cấu hình

### AI Agent Configuration

Vào **AI Assistant > Configuration** để cấu hình:

- **Anthropic API Key**: API key cho Claude
- **MCP Server URL**: URL của MCP server (mặc định: http://127.0.0.1:8000)
- **Test Connection**: Kiểm tra kết nối

## Kiến trúc

### Components

1. **MCP Server** (`mcp_server/odoo_mcp_server.py`)
   - Cung cấp tools, resources, prompts
   - Tích hợp với Odoo ORM
   - Xử lý user confirmation

2. **Fast-Agent Client**
   - Kết nối với MCP server
   - Xử lý tương tác với Claude
   - Quản lý conversation

3. **Odoo UI**
   - Wizard form cho chat interface
   - Configuration management
   - JavaScript cho tương tác động

### Tools Available

- `search_leads`: Tìm kiếm leads
- `get_top_customers`: Lấy top khách hàng
- `create_lead`: Tạo lead mới
- `create_customer`: Tạo khách hàng mới
- `get_sales_summary`: Báo cáo doanh số

### Resources Available

- `sales_schema`: Schema của database
- `sales_summary`: Tóm tắt doanh số hiện tại

## Development

### Chạy MCP Server độc lập

```bash
cd addons/ai_odoo_agent
python mcp_server/odoo_mcp_server.py
```

### Test với Fast-Agent CLI

```bash
fast-agent go --config fastagent.config.yaml
```

### Debug

Kiểm tra logs trong Odoo để debug:
- MCP server logs
- Fast-Agent logs
- Odoo application logs

## Troubleshooting

### Lỗi thường gặp

1. **MCP Server không khởi động**
   - Kiểm tra port 8000 có available không
   - Kiểm tra dependencies đã cài đặt

2. **API Key không hợp lệ**
   - Kiểm tra Anthropic API key
   - Kiểm tra environment variable

3. **Tools không hoạt động**
   - Kiểm tra kết nối MCP server
   - Kiểm tra Odoo environment

## License

LGPL-3

## Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request 