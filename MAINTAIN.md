# Hướng dẫn Bảo trì và Phát triển Dự án

Tài liệu này cung cấp thông tin cho các nhà phát triển muốn bảo trì hoặc đóng góp vào dự án "Trình Kết Xuất Point Cloud Nâng Cao với Open3D".

## Tổng quan Kiến trúc

Dự án được viết bằng Python và sử dụng chủ yếu thư viện Open3D cho các tác vụ xử lý và hiển thị point cloud, cùng với NumPy cho các thao tác số học.

Cấu trúc chính của code bao gồm:

1.  **Thiết lập Tham số:** Các biến toàn cục ở đầu script cho phép người dùng dễ dàng cấu hình các khía cạnh khác nhau của quá trình xử lý và hiển thị.
2.  **Hàm Tiện ích:** Các hàm được module hóa để thực hiện các tác vụ cụ thể như tải dữ liệu, ước lượng pháp tuyến, và áp dụng shading.
3.  **Hàm Callback:** Các hàm được thiết kế để đáp ứng các sự kiện nhấn phím trong Open3D Visualizer, cho phép tương tác người dùng (ví dụ: đổi màu, bật/tắt hiệu ứng).
4.  **Luồng Chính (`if __name__ == "__main__":`)**: Điều phối việc gọi các hàm tiện ích, khởi tạo visualizer, đăng ký callbacks, và chạy vòng lặp hiển thị chính.

## Quy trình Phát triển

1.  **Thiết lập Môi trường:**
    *   Đảm bảo bạn đã cài đặt Python (phiên bản 3.7 trở lên được khuyến nghị).
    *   Tạo một môi trường ảo (virtual environment) để quản lý các gói phụ thuộc:
        ```bash
        python -m venv venv
        source venv/bin/activate  # Linux/macOS
        venv\Scripts\activate    # Windows
        ```
    *   Cài đặt các thư viện từ `requirements.txt` (nếu có) hoặc cài đặt thủ công:
        ```bash
        pip install open3d numpy scipy
        ```

2.  **Chạy và Kiểm thử:**
    *   Sử dụng một file point cloud `.ply` mẫu (ví dụ, `1M_cloud.ply` hoặc một file nhỏ hơn để kiểm thử nhanh) và đặt đúng đường dẫn trong `POINT_CLOUD_FILE_PATH`.
    *   Chạy script và kiểm tra tất cả các tính năng tương tác (phím tắt).
    *   Theo dõi output trên console để phát hiện lỗi và thời gian thực thi của các khối.

3.  **Kiểm soát Phiên bản (Version Control):**
    *   Sử dụng Git để quản lý mã nguồn.
    *   Tạo các nhánh (branch) riêng cho các tính năng mới hoặc sửa lỗi.
    *   Viết commit messages rõ ràng và súc tích.
    *   Sử dụng Pull Requests để review code trước khi merge vào nhánh chính (ví dụ: `main` hoặc `master`).

4.  **Coding Style và Conventions:**
    *   Tuân theo PEP 8 (Style Guide for Python Code) để đảm bảo code dễ đọc và nhất quán.
    *   Viết comments rõ ràng cho các hàm và các đoạn code phức tạp.
    *   Sử dụng tên biến và hàm mang tính mô tả.

## Các Khu vực Code Chính Cần Chú Ý

*   **`preprocess_point_cloud_for_shading()`:** Logic ước lượng pháp tuyến. Chất lượng pháp tuyến ảnh hưởng lớn đến shading. Việc tính toán `radius` cho `KDTreeSearchParamHybrid` dựa trên `avg_dist` là một heuristic, có thể cần tinh chỉnh cho các loại dữ liệu khác nhau.
*   **`apply_enhanced_sun_shading()`:** Thuật toán shading chính. Các hằng số như `AMBIENT_STRENGTH`, `DIFFUSE_STRENGTH`, `SPECULAR_STRENGTH`, `SHININESS_FACTOR` và `SUN_DIRECTION` có thể được thử nghiệm để đạt được các hiệu ứng hình ảnh khác nhau. Cách tính `view_position` cho specular là một ước lượng và có thể được cải thiện nếu có thông tin camera chính xác hơn trong thời gian thực.
*   **Hàm Callbacks (`*_cb`):** Logic tương tác người dùng. Khi thêm phím tắt mới, cần đăng ký callback tương ứng với `vis.register_key_callback()`. Đảm bảo các biến toàn cục được xử lý đúng cách (sử dụng `global` nếu cần thay đổi giá trị của chúng).
*   **Thiết lập Camera trong `__main__`:** Việc tính toán `PinholeCameraIntrinsic` và cố gắng giữ lại `extrinsic` hiện tại là một nỗ lực để kiểm soát FOV. API camera của Open3D có thể hơi khó sử dụng cho việc thiết lập chính xác từng tham số.
*   **Quản lý Biến Toàn Cục:** Các biến như `global_vis`, `global_pcd_display`, `global_bg_is_dark`, `global_specular_on` được sử dụng để chia sẻ trạng thái với các hàm callback. Cần cẩn thận khi sửa đổi chúng.

## Gỡ lỗi (Debugging)

*   **Sử dụng `print()`:** Chèn các lệnh `print()` để theo dõi giá trị của biến và luồng thực thi.
*   **Open3D Visualizer:**
    *   Phím `C`: In thông số camera hiện tại ra console.
    *   Ctrl + Click vào điểm: In tọa độ và màu của điểm.
*   **Kiểm tra Pháp tuyến:** Bật hiển thị vector pháp tuyến (phím `N`) để kiểm tra xem chúng có được ước lượng và định hướng đúng không.
*   **Tách biệt Vấn đề:** Nếu một tính năng phức tạp không hoạt động, hãy thử tạo một script nhỏ hơn chỉ để kiểm thử riêng phần đó.

## Cải tiến Tiềm năng (Xem thêm trong README.md)

*   Tích hợp các thuật toán shading nâng cao hơn (ví dụ: Screen Space Ambient Occlusion nếu có thể).
*   Cho phép người dùng nhập các tham số (hướng mặt trời, màu sắc) qua giao diện dòng lệnh hoặc một file cấu hình.
*   Cải thiện hiệu năng cho các tác vụ nặng bằng cách tối ưu hóa NumPy hoặc xem xét các giải pháp tính toán song song/GPU.
*   Phát triển một GUI đơn giản (ví dụ với Tkinter, PyQt, hoặc Dear PyGui) để điều khiển dễ dàng hơn.

## Báo cáo Lỗi và Đề xuất Tính năng

*   Sử dụng mục "Issues" trên GitHub (nếu dự án được host trên đó) để báo cáo lỗi hoặc đề xuất tính năng mới.
*   Khi báo lỗi, cung cấp càng nhiều thông tin càng tốt:
    *   Phiên bản Open3D, NumPy, Python bạn đang sử dụng.
    *   Hệ điều hành.
    *   Các bước để tái tạo lỗi.
    *   Mô tả lỗi và output/traceback đầy đủ.
    *   File point cloud mẫu (nếu có thể và không quá lớn) để giúp tái tạo lỗi.

Bằng cách tuân theo các hướng dẫn này, chúng ta có thể giữ cho dự án được tổ chức tốt, dễ bảo trì và mở rộng trong tương lai.