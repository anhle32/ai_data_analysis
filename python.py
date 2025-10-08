# python.py

import streamlit as st
import pandas as pd
# from google import genai # Bỏ comment nếu bạn đã cài đặt và muốn dùng AI

# --- Cấu hình Trang Streamlit ---
st.set_page_config(
    page_title="App Phân Tích Báo Cáo Tài Chính",
    layout="wide"
)

st.title("Ứng dụng Phân Tích Báo Cáo Tài Chính 📊")

# --- Hàm tính toán chính (Tối ưu hóa bằng caching) ---
@st.cache_data
def process_financial_data(df):
    """Thực hiện các phép tính Tăng trưởng và Tỷ trọng."""
    
    # 1. Tính Tốc độ Tăng trưởng
    df['Tốc độ tăng trưởng (%)'] = (
        (df['Năm sau'] - df['Năm trước']) / df['Năm trước'].replace(0, 1e-9)
    ) * 100

    # 2. Tính Tỷ trọng theo Tổng Tài sản
    # Giả định: Hàng "TỔNG CỘNG TÀI SẢN" luôn tồn tại
    try:
        tong_tai_san_N_1 = df[df['Chỉ tiêu'].str.contains('TỔNG CỘNG TÀI SẢN', case=False, na=False)]['Năm trước'].iloc[0]
        tong_tai_san_N = df[df['Chỉ tiêu'].str.contains('TỔNG CỘNG TÀI SẢN', case=False, na=False)]['Năm sau'].iloc[0]
    except IndexError:
        st.error("Không tìm thấy chỉ tiêu 'TỔNG CỘNG TÀI SẢN' trong file.")
        return None

    df['Tỷ trọng Năm trước (%)'] = (df['Năm trước'] / tong_tai_san_N_1) * 100
    df['Tỷ trọng Năm sau (%)'] = (df['Năm sau'] / tong_tai_san_N) * 100
    
    return df

# --- Chức năng 1: Tải File ---
uploaded_file = st.file_uploader(
    "1. Tải file Excel Báo cáo Tài chính (Chỉ tiêu | Năm trước | Năm sau)",
    type=['xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file)
        st.success("Tải file thành công!")
        
        # Tiền xử lý (đảm bảo tên cột chuẩn)
        df_raw.columns = ['Chỉ tiêu', 'Năm trước', 'Năm sau']
        
        # Xử lý dữ liệu
        df_processed = process_financial_data(df_raw.copy())

        if df_processed is not None:
            
            st.subheader("2. & 3. Kết quả Tăng trưởng và Tỷ trọng")
            st.dataframe(df_processed.style.format({
                'Năm trước': '{:,.0f}',
                'Năm sau': '{:,.0f}',
                'Tốc độ tăng trưởng (%)': '{:.2f}%',
                'Tỷ trọng Năm trước (%)': '{:.2f}%',
                'Tỷ trọng Năm sau (%)': '{:.2f}%'
            }), use_container_width=True)
            
            # --- Chức năng 4: Tính Chỉ số Tài chính (Ví dụ) ---
            st.subheader("4. Các Chỉ số Tài chính Cơ bản")
            
            # Giả lập lấy giá trị (Cần thay thế bằng logic lọc thực tế từ df_processed)
            try:
                # Ví dụ tính Thanh toán Hiện hành (Cần lọc Nợ ngắn hạn từ file thực tế)
                tai_san_ngan_han_N = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]
                tai_san_ngan_han_N_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]

                # TẠM DÙNG giá trị cố định cho Nợ Ngắn Hạn để demo logic
                # Trong thực tế, bạn phải lọc chỉ tiêu Nợ Ngắn Hạn từ BCĐKT
                no_ngan_han_N = 800  
                no_ngan_han_N_1 = 600

                thanh_toan_hien_hanh_N = tai_san_ngan_han_N / no_ngan_han_N
                thanh_toan_hien_hanh_N_1 = tai_san_ngan_han_N_1 / no_ngan_han_N_1
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Chỉ số Thanh toán Hiện hành (Năm trước)",
                        value=f"{thanh_toan_hien_hanh_N_1:.2f} lần"
                    )
                with col2:
                    st.metric(
                        label="Chỉ số Thanh toán Hiện hành (Năm sau)",
                        value=f"{thanh_toan_hien_hanh_N:.2f} lần",
                        delta=f"{thanh_toan_hien_hanh_N - thanh_toan_hien_hanh_N_1:.2f}"
                    )
                    
            except IndexError:
                 st.warning("Không đủ dữ liệu để tính Chỉ số Thanh toán Hiện hành (Thiếu TÀI SẢN NGẮN HẠN hoặc NỢ NGẮN HẠN).")
                 
            # --- Chức năng 5: Nhận xét AI ---
            st.subheader("5. Nhận xét Tình hình Tài chính (AI)")
            if st.button("Yêu cầu AI Phân tích"):
                
                # --- PHẦN BẠN CẦN CHỈNH SỬA VỚI GENAI ---
                # Kiểm tra secrets và gọi API Gemini tại đây
                
                # Dữ liệu mẫu để tạo prompt
                data_for_ai = {
                    'Tăng trưởng Tài sản ngắn hạn': f"{df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Tốc độ tăng trưởng (%)'].iloc[0]:.2f}%",
                    'Thanh toán hiện hành N-1': f"{thanh_toan_hien_hanh_N_1:.2f}",
                    'Thanh toán hiện hành N': f"{thanh_toan_hien_hanh_N:.2f}"
                }
                
                # Đây là output giả lập, thay thế bằng hàm gọi API thực tế
                with st.spinner('Đang chờ Gemini phân tích...'):
                    st.info("""
                    **[KẾT QUẢ GIẢ LẬP]**

                    Dựa trên dữ liệu, tài sản ngắn hạn có tốc độ tăng trưởng tốt. 
                    Chỉ số Thanh toán Hiện hành đã cải thiện từ {thanh_toan_hien_hanh_N_1:.2f} lên {thanh_toan_hien_hanh_N:.2f}, cho thấy khả năng thanh toán ngắn hạn của doanh nghiệp được củng cố. Tuy nhiên, cần xem xét chất lượng của tài sản ngắn hạn để đánh giá chính xác hơn về tính thanh khoản.
                    """)
                # ---------------------------------------------

    except Exception as e:
        st.error(f"Có lỗi xảy ra khi đọc hoặc xử lý file: {e}")

else:
    st.info("Vui lòng tải lên file Excel để bắt đầu phân tích.")
