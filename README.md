
# Trình Kết Xuất Point Cloud Nâng Cao với Open3D  
*Phát triển bởi Nguyễn Ngọc Phúc và Mai Thế Duy*

## Giới thiệu

Đây là một công cụ mã nguồn mở được phát triển nhằm trực quan hóa các tập dữ liệu point cloud dung lượng lớn (ví dụ: 1 triệu điểm) dưới định dạng `.ply`, sử dụng thư viện đồ họa **Open3D** trên nền tảng Python. Dự án kết hợp giữa kỹ thuật lập trình, toán học ứng dụng và hình học tính toán để mang đến trải nghiệm hiển thị chất lượng cao cho người dùng.

Với mục tiêu nâng cao khả năng cảm nhận cấu trúc bề mặt mà không cần mesh hóa dữ liệu, phần mềm tích hợp các hiệu ứng chiếu sáng nâng cao như **Eye-Dome Lighting (EDL)** và **Sun-like Shading**, giúp người dùng dễ dàng phân biệt các vùng lồi/lõm trong mô hình 3D.

---

## Mục tiêu chính

- Hỗ trợ tải và hiển thị point cloud dung lượng lớn.
- Tự động tiền xử lý pháp tuyến nếu chưa có.
- Áp dụng các hiệu ứng shading nâng cao để tăng độ tương phản và chiều sâu.
- Cho phép tùy chỉnh màu sắc, kích thước điểm, và giao diện hiển thị thông qua các phím tắt.
- Đo thời gian thực thi để đánh giá hiệu năng hệ thống.

---

## Tính năng nổi bật

✅ Hỗ trợ file đầu vào định dạng `.ply`  
✅ Ước lượng pháp tuyến tự động  
✅ Hiệu ứng ánh sáng Eye-Dome Lighting (EDL)  
✅ Sun-like Shading với thành phần Ambient/Diffuse/Specular  
✅ Tương tác trực tiếp trong cửa sổ Open3D Visualizer:  
  🔹 Thay đổi màu nền  
  🔹 Chuyển đổi màu sắc điểm  
  🔹 Bật/tắt specular  
  🔹 Điều chỉnh kích thước điểm  
✅ Đo thời gian thực thi các bước xử lý chính  

---

## Công nghệ sử dụng

- **Ngôn ngữ lập trình**: Python 3.7+
- **Thư viện chính**:
  - `open3d`: Thư viện đồ họa 3D mã nguồn mở
  - `numpy`: Xử lý mảng số hiệu quả
  - `scipy`: Hỗ trợ tính toán khoa học

```bash
pip install open3d numpy scipy
```

---

## Hướng dẫn sử dụng

1. Đảm bảo bạn có file point cloud định dạng `.ply`.
2. Mở script Python (`render_pcd.py`) và thiết lập đường dẫn tới file point cloud.
3. Chạy chương trình:
   ```bash
   python render_pcd.py
   ```
4. Sử dụng các phím tắt trong cửa sổ Open3D để tương tác:
   - `L`: Bật/tắt chế độ EDL
   - `B`: Chuyển đổi màu nền
   - `X`: Thay đổi màu cơ bản của point cloud
   - `K`: Bật/tắt hiệu ứng specular
   - `+` / `P`: Tăng kích thước điểm
   - `-` / `M`: Giảm kích thước điểm
   - `Q`: Thoát chương trình

---

## Hạn chế hiện tại & Hướng phát triển

### Hạn chế
- Không hỗ trợ đổ bóng thật (real-time shadows)
- Hiệu năng có thể giảm với point cloud cực lớn khi shading thủ công được bật
- Các tham số EDL khó tinh chỉnh sâu

### Hướng cải tiến tiềm năng
- Tối ưu hóa shading bằng GPU
- Phát triển giao diện người dùng đồ họa (GUI)
- Tích hợp thêm hiệu ứng nâng cao và khả năng xuất ảnh/video

---

## Đóng góp

Chúng tôi rất hoan nghênh mọi sự đóng góp từ cộng đồng để cùng phát triển phần mềm ngày càng hoàn thiện và hữu ích hơn! Dù bạn là nhà phát triển, nhà nghiên cứu, sinh viên hay người quan tâm đến đồ họa máy tính và xử lý dữ liệu điểm – bạn đều có thể góp phần của mình vào dự án.


Nếu bạn muốn cùng cải tiến phần mềm, vui lòng:
- ✅ Tạo **Pull Request** với các cập nhật mã nguồn hoặc tính năng mới.
- 🛠 Mở **Issue** để báo lỗi hoặc đề xuất cải tiến.

Cảm ơn bạn đã góp phần làm cho công cụ này trở nên hữu ích hơn mỗi ngày!

---

## Giấy phép

Dự án được cấp phép theo **Giấy phép MIT** – một giấy phép mã nguồn mở linh hoạt và phổ biến. Bạn có thể xem chi tiết trong file `LICENSE`.

