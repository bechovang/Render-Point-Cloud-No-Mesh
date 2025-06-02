import open3d as o3d
import numpy as np
import os
import time
# scipy không còn cần thiết nữa
# from scipy.optimize import least_squares
# from scipy.special import comb

# --- CÀI ĐẶT THAM SỐ ---
POINT_CLOUD_FILE_PATH = "1M_cloud.ply" # <<< THAY ĐỔI ĐƯỜNG DẪN NÀY

# Tham số cho ước lượng pháp tuyến
NORMAL_ESTIMATION_RADIUS_FACTOR = 1.0
NORMAL_ESTIMATION_MAX_NN = 30
ORIENT_NORMALS_K = 15

# Tham số cho shading (Sun-like)
# Sẽ luôn áp dụng một dạng shading dựa trên pháp tuyến để tăng cảm giác khối
# APPLY_MANUAL_SHADING sẽ quyết định có dùng specular phức tạp hay không
APPLY_FULL_MANUAL_SHADING_WITH_SPECULAR = True # True để dùng specular, False cho diffuse + ambient đơn giản
SUN_DIRECTION = np.array([-0.6, -0.7, -1.0]) # Hướng mặt trời chiếu từ trên, hơi nghiêng trái và trước
                                            # Vector này trỏ TỪ điểm tới mặt trời
AMBIENT_STRENGTH = 0.2                      # Ánh sáng môi trường cơ bản
DIFFUSE_STRENGTH = 0.8                      # Ảnh hưởng của ánh sáng trực tiếp
SPECULAR_STRENGTH = 0.6                     # Độ mạnh của phản xạ gương (nếu bật)
SHININESS_FACTOR = 64                       # Độ "bóng" của bề mặt

# Tham số cho visualizer
INITIAL_POINT_SIZE = 2.0 # Tăng kích thước điểm để giảm xuyên thấu và tăng hiệu ứng EDL
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
INITIAL_BACKGROUND_IS_DARK = True
CAMERA_FIELD_OF_VIEW_DEG = 60

# --- BIẾN TOÀN CỤC CHO CALLBACK MÀU NỀN ---
global_bg_is_dark = INITIAL_BACKGROUND_IS_DARK
DARK_BG_COLOR = np.array([0.1, 0.1, 0.1])  # Tối hơn một chút nữa
LIGHT_BG_COLOR = np.array([0.9, 0.9, 0.9]) # Sáng hơn một chút

# --- HÀM TIỆN ÍCH ---
def load_point_cloud(filepath):
    # ... (Giữ nguyên) ...
    if not os.path.exists(filepath):
        print(f"Lỗi: File không tồn tại tại '{filepath}'")
        return None
    try:
        print(f"Đang tải point cloud từ: {filepath}...")
        pcd = o3d.io.read_point_cloud(filepath)
        if not pcd.has_points():
            print("Lỗi: Point cloud rỗng sau khi tải.")
            return None
        print(f"Tải thành công: {len(pcd.points)} điểm.")
        return pcd
    except Exception as e:
        print(f"Lỗi khi tải point cloud: {e}")
        return None

def preprocess_point_cloud_for_shading(pcd, radius_factor, max_nn, orient_k):
    """Ước lượng pháp tuyến và đảm bảo PCD có màu cơ bản."""
    if not pcd.has_normals():
        print("Point cloud chưa có pháp tuyến. Đang ước lượng...")
        start_time = time.time()
        if len(pcd.points) > max_nn:
            try:
                print("  Tính toán khoảng cách lân cận...")
                sample_count_for_dist = min(len(pcd.points), 100000)
                if len(pcd.points) > sample_count_for_dist:
                    print(f"  PCD có {len(pcd.points)} điểm, ước lượng avg_dist trên {sample_count_for_dist} điểm ngẫu nhiên.")
                    indices = np.random.choice(len(pcd.points), sample_count_for_dist, replace=False)
                    pcd_sample_for_dist = pcd.select_by_index(indices)
                else:
                    pcd_sample_for_dist = pcd
                distances = pcd_sample_for_dist.compute_nearest_neighbor_distance()
                avg_dist = np.mean(distances)
                radius = avg_dist * radius_factor
                print(f"  Khoảng cách lân cận TB (ước lượng): {avg_dist:.4f}, Radius pháp tuyến: {radius:.4f}")
                if radius < 0.0001:
                    print(f"  Cảnh báo: Radius tính toán quá nhỏ ({radius:.6f}). Sử dụng fallback 0.005.")
                    radius = 0.005
            except Exception as e_dist:
                print(f"  Lỗi tính avg_dist: {e_dist}. Sử dụng radius mặc định (0.01).")
                radius = 0.01
        else:
            print(f"  PCD quá ít điểm. Sử dụng radius mặc định (0.01).")
            radius = 0.01
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
        print("  Đang định hướng pháp tuyến...")
        # Đảm bảo pháp tuyến hướng ra ngoài nếu có thể (khó cho point cloud thuần túy)
        # pcd.orient_normals_to_align_with_direction(orientation_reference=np.array([0.0,0.0,1.0]))
        pcd.orient_normals_consistent_tangent_plane(orient_k)
        end_time = time.time()
        if not pcd.has_normals():
            print("  Ước lượng pháp tuyến thất bại.")
        else:
            print(f"  Đã ước lượng pháp tuyến ({end_time - start_time:.2f}s).")
    else:
        print("Point cloud đã có pháp tuyến.")

    # Gán màu cơ bản nếu chưa có, hoặc đảm bảo màu không quá tối
    if not pcd.has_colors():
        print("Point cloud chưa có màu. Gán màu xám sáng mặc định.")
        pcd.paint_uniform_color([0.75, 0.75, 0.75]) # Màu xám sáng hơn
    else:
        # Kiểm tra nếu màu quá tối, có thể tăng độ sáng một chút
        colors = np.asarray(pcd.colors)
        if np.mean(colors) < 0.1: # Nếu trung bình màu rất tối
            print("Màu gốc của point cloud rất tối, tăng nhẹ độ sáng cơ bản.")
            colors = np.clip(colors + 0.15, 0, 1) # Tăng sáng và clip
            pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd

def apply_enhanced_sun_shading(pcd, sun_dir, view_pos,
                               ambient_s, diffuse_s, specular_s=0.0, shininess=32.0,
                               use_specular=False):
    """
    Áp dụng shading dựa trên hướng mặt trời.
    Nếu use_specular=True, sẽ thêm thành phần specular.
    """
    if not pcd.has_normals():
        print("Cảnh báo: Shading cần pháp tuyến.")
        return pcd

    print(f"Đang áp dụng shading (Specular: {use_specular})...")
    # Vector L trỏ TỪ điểm tới nguồn sáng
    light_vector = -np.array(sun_dir) / np.linalg.norm(sun_dir)

    normals = np.asarray(pcd.normals)
    points = np.asarray(pcd.points)

    # Chuẩn hóa pháp tuyến
    norm_lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    valid_normals_mask = norm_lengths.flatten() > 1e-9 # Tránh chia cho zero
    normals_normalized = np.zeros_like(normals)
    if np.any(valid_normals_mask):
        normals_normalized[valid_normals_mask] = normals[valid_normals_mask] / norm_lengths[valid_normals_mask]

    # Diffuse component (Lambertian)
    # N.L = dot(normal, light_vector)
    diffuse_intensity = np.sum(normals_normalized * light_vector, axis=1)
    # Chỉ những mặt hướng về phía ánh sáng mới nhận diffuse
    diffuse_contrib = np.maximum(0, diffuse_intensity) * diffuse_s

    # Tính toán cường độ tổng hợp
    shaded_intensities = ambient_s + diffuse_contrib

    # Specular component (Blinn-Phong) - Tùy chọn
    if use_specular:
        # Vector V trỏ TỪ điểm tới camera/người xem
        view_vector_to_points = view_pos - points
        view_vector_norm = view_vector_to_points / (np.linalg.norm(view_vector_to_points, axis=1, keepdims=True) + 1e-9)
        
        # Vector H (halfway vector)
        half_vector = (light_vector + view_vector_norm)
        half_vector_norm = half_vector / (np.linalg.norm(half_vector, axis=1, keepdims=True) + 1e-9)
        
        # N.H = dot(normal, half_vector)
        spec_angle = np.sum(normals_normalized * half_vector_norm, axis=1)
        specular_contrib = specular_s * np.power(np.maximum(0, spec_angle), shininess)
        shaded_intensities += specular_contrib

    shaded_intensities = np.clip(shaded_intensities, 0, 1) # Đảm bảo cường độ trong khoảng [0,1]

    # Áp dụng cường độ vào màu gốc hoặc tạo màu xám nếu không có màu gốc
    if pcd.has_colors():
        original_colors = np.asarray(pcd.colors)
        new_colors = original_colors * shaded_intensities[:, np.newaxis] # Nhân với từng kênh R,G,B
    else: # Tạo màu xám dựa trên cường độ
        new_colors = np.tile(shaded_intensities[:, np.newaxis], (1, 3))

    pcd_shaded = o3d.geometry.PointCloud()
    pcd_shaded.points = o3d.utility.Vector3dVector(points)
    pcd_shaded.colors = o3d.utility.Vector3dVector(np.clip(new_colors, 0, 1))
    pcd_shaded.normals = o3d.utility.Vector3dVector(normals) # Giữ lại pháp tuyến
    print("Đã áp dụng shading.")
    return pcd_shaded


# --- CALLBACK CHO VISUALIZER ---
def toggle_background_color(vis):
    global global_bg_is_dark
    opt = vis.get_render_option()
    if global_bg_is_dark:
        opt.background_color = LIGHT_BG_COLOR
        global_bg_is_dark = False
        print("Đổi màu nền sang SÁNG.")
    else:
        opt.background_color = DARK_BG_COLOR
        global_bg_is_dark = True
        print("Đổi màu nền sang TỐI.")
    # vis.update_renderer() # Có thể cần thiết ở một số phiên bản để thấy thay đổi ngay
    return False

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    print("--- Point Cloud Enhanced Lighting Renderer ---")

    pcd_original = load_point_cloud(POINT_CLOUD_FILE_PATH)
    if pcd_original is None:
        exit()

    # Tạo bản sao để xử lý, giữ lại pcd_original nếu cần
    pcd_processed = o3d.geometry.PointCloud(pcd_original)

    pcd_processed = preprocess_point_cloud_for_shading(pcd_processed,
                                                       radius_factor=NORMAL_ESTIMATION_RADIUS_FACTOR,
                                                       max_nn=NORMAL_ESTIMATION_MAX_NN,
                                                       orient_k=ORIENT_NORMALS_K)

    # Ước lượng vị trí camera (cần cho specular và để đặt view ban đầu)
    # Chúng ta sẽ sử dụng vị trí này cho cả shading thủ công và thiết lập view ban đầu
    bbox = pcd_processed.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    extent = bbox.get_extent()
    max_extent = np.max(extent)
    if max_extent < 1e-6: max_extent = 1.0 # Tránh bbox quá nhỏ

    # Vị trí camera ước lượng: lùi ra xa theo hướng trung bình của các pháp tuyến
    # hoặc đơn giản là lùi ra theo một trục cố định so với tâm bbox.
    # Đây là một heuristic, bạn có thể cần điều chỉnh.
    # Lùi ra xa gấp 2-3 lần kích thước lớn nhất của bbox.
    # Hướng lùi: có thể là [0,0,1] (nhìn từ +Z), hoặc phức tạp hơn.
    # Chúng ta sẽ dùng một vị trí tổng quát hơn.
    camera_distance_factor = 2.5
    # Vị trí camera ước lượng để nhìn vào tâm
    # view_position_est = center + np.array([max_extent * 0.5, -max_extent * 1.0, max_extent * camera_distance_factor * 0.8])
    # Đơn giản hơn:
    view_position_est = center + np.array([0.0, 0.0, max_extent * camera_distance_factor])


    # Áp dụng shading dựa trên pháp tuyến (Sun-like)
    # Hàm này sẽ tạo ra pcd_display với màu đã được tô bóng.
    pcd_display = apply_enhanced_sun_shading(pcd_processed, # Dùng pcd_processed đã có pháp tuyến
                                       sun_dir=SUN_DIRECTION,
                                       view_pos=view_position_est, # Cần cho specular
                                       ambient_s=AMBIENT_STRENGTH,
                                       diffuse_s=DIFFUSE_STRENGTH,
                                       specular_s=SPECULAR_STRENGTH,
                                       shininess=SHININESS_FACTOR,
                                       use_specular=APPLY_FULL_MANUAL_SHADING_WITH_SPECULAR)


    geometries_to_draw = [pcd_display]
    # (Phần cắt mặt phẳng và Bezier đã được loại bỏ theo yêu cầu)

    print("\n--- KHỞI ĐỘNG OPEN3D VISUALIZER ---")
    print("Trong cửa sổ hiển thị, hãy thử các thao tác sau:")
    print("  - Kéo chuột trái: Xoay camera.")
    print("  - Lăn chuột: Zoom.")
    print("  - Kéo chuột phải / Shift + Kéo chuột trái: Di chuyển camera (Pan).")
    print("  - Phím 'L': Chuyển đổi giữa các chế độ chiếu sáng. **TÌM CHẾ ĐỘ EDL (EYE-DOME LIGHTING)**.")
    print("             EDL thường cho hiệu ứng chiều sâu TỐT NHẤT cho point cloud.")
    print("  - Phím 'B': Đổi màu nền (Sáng/Tối).")
    print("  - Phím 'S': Chuyển đổi giữa các kiểu tô bóng (ít ảnh hưởng hơn EDL).")
    print("  - Phím 'N': Bật/tắt hiển thị pháp tuyến (vector).")
    print("  - Phím 'P' / '+': Tăng kích thước điểm.")
    print("  - Phím 'M' / '-': Giảm kích thước điểm.")
    print("  - Phím 'C': In thông số camera ra console.")
    print("  - Ctrl + Left Click vào điểm: In thông tin điểm ra console.")
    print("  - Phím 'R': Reset view về mặc định (có thể không giữ FOV đã set).")
    print("  - Phím 'Q' hoặc đóng cửa sổ: Thoát.")

    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window(window_name="Enhanced Point Cloud Lighting (Focus on Sun & EDL)",
                             width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    for geom in geometries_to_draw:
        vis.add_geometry(geom)
    
    render_option = vis.get_render_option()
    if INITIAL_BACKGROUND_IS_DARK:
        render_option.background_color = DARK_BG_COLOR
    else:
        render_option.background_color = LIGHT_BG_COLOR
        global_bg_is_dark = False

    render_option.point_size = INITIAL_POINT_SIZE
    # render_option.light_on = True # Shading thủ công đã xử lý ánh sáng,
                                 # nhưng nguồn sáng mặc định của O3D có thể vẫn cần cho EDL nếu nó sử dụng.
                                 # Thử bật/tắt để xem ảnh hưởng. Nếu shading thủ công đã đẹp, có thể đặt False.
    render_option.light_on = False # Ưu tiên shading thủ công của chúng ta. EDL không phụ thuộc vào light_on này.


    vis.register_key_callback(ord('B'), toggle_background_color)

    # --- Thiết lập Camera Parameters với FOV và vị trí ban đầu ---
    view_control = vis.get_view_control()
    
    # Tính toán intrinsic từ FOV
    fov_rad = np.deg2rad(CAMERA_FIELD_OF_VIEW_DEG)
    fy = WINDOW_HEIGHT / (2 * np.tan(fov_rad / 2.0))
    fx = fy # Giả sử pixel vuông
    cx = WINDOW_WIDTH / 2.0
    cy = WINDOW_HEIGHT / 2.0
    intrinsic_matrix = o3d.camera.PinholeCameraIntrinsic(WINDOW_WIDTH, WINDOW_HEIGHT, fx, fy, cx, cy)

    # Xây dựng extrinsic matrix (vị trí và hướng camera)
    # Camera sẽ ở vị trí view_position_est, nhìn vào tâm của bbox
    # Up vector thường là [0, 1, 0] (trục Y dương hướng lên)
    # Tuy nhiên, nếu mô hình của bạn có hướng "lên" khác, bạn cần điều chỉnh up vector.
    # Open3D dùng look_at(center, eye, up)
    # center: điểm camera nhìn vào (target)
    # eye: vị trí camera
    # up: vector hướng lên của camera
    
    # Tạo một đối tượng PinholeCameraParameters
    cam_params = o3d.camera.PinholeCameraParameters()
    cam_params.intrinsic = intrinsic_matrix
    
    # Tạo ma trận extrinsic từ look_at
    # Open3D không có hàm look_at trực tiếp để tạo extrinsic matrix,
    # nhưng view_control.set_lookat, set_front, set_up sẽ làm điều đó ngầm.
    # Chúng ta sẽ thiết lập qua ViewControl sau khi nó được khởi tạo.
    
    # Cần chạy poll_events và update_renderer để các đối tượng được load hoàn toàn
    # và các giá trị camera ban đầu của visualizer được thiết lập trước khi chúng ta thay đổi chúng.
    vis.poll_events()
    vis.update_renderer()

    # Đặt vị trí camera và hướng nhìn
    # print(f"Đặt camera: eye={np.round(view_position_est,2)}, center={np.round(center,2)}, up=[0,1,0]")
    # view_control.set_lookat(center) # Nhìn vào tâm bbox
    # view_control.set_front(-(view_position_est - center) / np.linalg.norm(view_position_est - center)) # Hướng từ eye đến center
    # view_control.set_up(np.array([0.0, 1.0, 0.0])) # Y là up, nếu mô hình của bạn có trục Z là up, đổi thành [0,0,1]
    # view_control.set_zoom(0.7) # Điều chỉnh zoom ban đầu

    # Cách tốt hơn để đặt camera là lấy params hiện tại, sửa intrinsic, rồi đặt lại.
    current_pinhole_params = view_control.convert_to_pinhole_camera_parameters()
    # Chúng ta muốn giữ extrinsic mà Open3D tự tính để đảm bảo nhìn thấy vật thể
    current_extrinsic = current_pinhole_params.extrinsic
    
    new_cam_params = o3d.camera.PinholeCameraParameters()
    new_cam_params.intrinsic = intrinsic_matrix # Intrinsic mới với FOV mong muốn
    new_cam_params.extrinsic = current_extrinsic  # Giữ lại vị trí và hướng camera Open3D đã tự đặt
    
    view_control.convert_from_pinhole_camera_parameters(new_cam_params, allow_arbitrary=True)
    
    print(f"  Đã cố gắng đặt Field of View ~{CAMERA_FIELD_OF_VIEW_DEG} độ.")

    print("\nVisualizer đang chạy. Hãy thử các phím điều khiển (B, L, P, M,...).")
    vis.run()
    vis.destroy_window()

    print("\n--- Kết thúc hiển thị ---")