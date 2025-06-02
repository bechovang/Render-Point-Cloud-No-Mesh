
# Trình Kết Xuất Point Cloud Nâng Cao với Open3D

Dự án này cung cấp một script Python để tải, tiền xử lý và hiển thị các tệp point cloud (.ply) lớn (ví dụ: 1 triệu điểm) bằng thư viện Open3D. Mục tiêu chính là cung cấp các hiệu ứng shading nâng cao, bao gồm mô phỏng ánh sáng mặt trời và Eye-Dome Lighting (EDL), để làm nổi bật cấu trúc lồi/lõm của point cloud mà không cần phải tái tạo thành mesh. Script cũng bao gồm các tính năng tương tác như thay đổi màu nền và màu cơ bản của point cloud, bật/tắt hiệu ứng specular, và đo thời gian thực thi của các bước xử lý chính.

## Tính năng chính

*   **Tải Point Cloud:** Hỗ trợ tải các tệp `.ply`.
*   **Ước lượng Pháp tuyến:** Tự động tính toán và định hướng pháp tuyến cho point cloud nếu chưa có, một bước quan trọng cho các hiệu ứng shading.
*   **Shading Nâng cao:**
    *   **Mô phỏng Ánh sáng Mặt trời (Sun-like Shading):** Áp dụng mô hình chiếu sáng bao gồm các thành phần ambient, diffuse, và specular (có thể bật/tắt) để tạo cảm giác khối và chi tiết bề mặt.
    *   **Tận dụng Eye-Dome Lighting (EDL):** Hướng dẫn người dùng kích hoạt EDL trong Open3D Visualizer để tăng cường đáng kể cảm nhận chiều sâu và cấu trúc.
*   **Tùy chỉnh Hiển thị Tương tác:**
    *   **Thay đổi màu nền:** Chuyển đổi giữa nền sáng và tối bằng phím tắt.
    *   **Thay đổi màu cơ bản của Point Cloud:** Duyệt qua một danh sách các màu cơ bản được định sẵn (bao gồm cả màu gốc của file nếu có) bằng phím tắt.
    *   **Bật/Tắt Specular:** Kiểm soát thành phần phản xạ gương của shading thủ công.
    *   **Điều chỉnh kích thước điểm:** Tăng/giảm kích thước điểm để có hiển thị tốt nhất.
*   **Thiết lập Camera:** Cố gắng thiết lập Field of View (FOV) ban đầu cho camera.
*   **Đo thời gian thực thi:** In ra thời gian xử lý cho các bước chính, giúp người dùng theo dõi và đánh giá hiệu năng.
*   **Dễ sử dụng:** Cung cấp hướng dẫn rõ ràng trong console về các phím tắt và cách tương tác với visualizer.

## Yêu cầu Hệ thống và Cài đặt

*   Python 3.7+
*   Các thư viện Python:
    *   `open3d`
    *   `numpy`
    *   `scipy` (Mặc dù phần Bezier đã bị loại bỏ, `comb` vẫn được import. Có thể loại bỏ nếu không cần thiết cho các tính năng khác trong tương lai).

Bạn có thể cài đặt các thư viện cần thiết bằng pip:

```bash
pip install open3d numpy scipy
```

Hoặc nếu bạn có file `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Cách sử dụng

1.  **Chuẩn bị file Point Cloud:** Đảm bảo bạn có một file point cloud định dạng `.ply` (ví dụ: `1M_cloud.ply`).
2.  **Cấu hình Script:**
    *   Mở file script Python (ví dụ: `render_pcd.py`).
    *   Thay đổi giá trị của biến `POINT_CLOUD_FILE_PATH` ở đầu script để trỏ đến file point cloud của bạn.
    *   Bạn có thể tinh chỉnh các tham số khác trong phần "CÀI ĐẶT THAM SỐ" như:
        *   `NORMAL_ESTIMATION_*`: Tham số cho việc ước lượng pháp tuyến.
        *   `APPLY_ENHANCED_SHADING`, `SUN_DIRECTION`, `AMBIENT_STRENGTH`, v.v.: Tham số cho shading thủ công.
        *   `INITIAL_POINT_SIZE`, `WINDOW_WIDTH`, `WINDOW_HEIGHT`, `CAMERA_FIELD_OF_VIEW_DEG`: Tham số cho visualizer.
3.  **Chạy Script:**
    Thực thi script từ terminal:
    ```bash
    python render_pcd.py
    ```
4.  **Tương tác với Cửa sổ Open3D Visualizer:**
    *   Một cửa sổ sẽ xuất hiện hiển thị point cloud.
    *   Sử dụng các phím tắt được hướng dẫn trong console để tương tác:
        *   **`L`**: Bật/tắt và duyệt qua các chế độ chiếu sáng. **Hãy tìm và kích hoạt Eye-Dome Lighting (EDL)** để có hiệu ứng chiều sâu tốt nhất.
        *   **`B`**: Đổi màu nền (sáng/tối).
        *   **`X`**: Duyệt qua các màu cơ bản của point cloud.
        *   **`K`**: Bật/tắt hiệu ứng specular (nếu `APPLY_ENHANCED_SHADING` là `True`).
        *   **`P` / `+`**: Tăng kích thước điểm.
        *   **`M` / `-`**: Giảm kích thước điểm.
        *   **Chuột trái + Kéo**: Xoay camera.
        *   **Chuột phải + Kéo / Shift + Chuột trái + Kéo**: Di chuyển camera (Pan).
        *   **Lăn chuột**: Zoom.
        *   **`Q` / Đóng cửa sổ**: Thoát.

## Cấu trúc Code

*   **CÀI ĐẶT THAM SỐ:** Định nghĩa các hằng số và tham số cấu hình cho script.
*   **BIẾN TOÀN CỤC CHO CALLBACKS:** Các biến cần thiết cho các hàm callback của visualizer.
*   **HÀM TIỆN ÍCH:**
    *   `load_point_cloud()`: Tải point cloud từ file.
    *   `preprocess_point_cloud_for_shading()`: Ước lượng pháp tuyến và gán màu cơ bản.
    *   `apply_enhanced_sun_shading()`: Áp dụng thuật toán shading thủ công.
*   **CALLBACKS CHO VISUALIZER:**
    *   `toggle_background_color_cb()`: Thay đổi màu nền.
    *   `_refresh_shading()`: Hàm nội bộ để áp dụng lại shading.
    *   `cycle_base_color_cb()`: Duyệt qua các màu cơ bản.
    *   `toggle_specular_cb()`: Bật/tắt specular.
*   **CHƯƠNG TRÌNH CHÍNH (`if __name__ == "__main__":`)**
    *   Điều phối toàn bộ quy trình: tải dữ liệu, tiền xử lý, áp dụng shading ban đầu, khởi tạo visualizer, đăng ký callbacks, và chạy vòng lặp hiển thị.

## Hạn chế và Cải tiến Tiềm năng

*   **Đổ bóng thực sự (Cast Shadows):** Script hiện tại không tạo ra bóng đổ thực sự giữa các phần của point cloud. Điều này yêu cầu các kỹ thuật rendering phức tạp hơn.
*   **Hiệu năng Shading thủ công:** Với point cloud rất lớn, việc tính toán shading thủ công trên CPU cho mỗi frame (nếu camera di chuyển và `view_position` thay đổi liên tục) có thể chậm. Shading trên GPU sẽ hiệu quả hơn nhiều.
*   **Sắp xếp điểm cắt mặt phẳng:** Heuristic sắp xếp điểm sau khi cắt mặt phẳng (đã bị loại bỏ trong phiên bản hiện tại) rất đơn giản và có thể không hoạt động tốt cho các đường cắt phức tạp.
*   **Can thiệp sâu vào EDL:** Việc tinh chỉnh các tham số nội tại của EDL trong Open3D có thể khó khăn.
*   **Giao diện người dùng đồ họa (GUI):** Để có trải nghiệm người dùng tốt hơn, có thể phát triển một GUI thay vì chỉ dựa vào phím tắt console.

## Đóng góp

Nếu bạn có ý tưởng cải tiến hoặc muốn đóng góp, vui lòng tạo Pull Request hoặc mở một Issue.

## Giấy phép

Dự án này được cấp phép theo Giấy phép MIT. Xem file `LICENSE` (nếu có) để biết chi tiết.
(Bạn nên thêm một file `LICENSE` nếu muốn, ví dụ giấy phép MIT là phổ biến cho các dự án nguồn mở).



