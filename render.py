import open3d as o3d
import numpy as np
import os
import time

# --- CÀI ĐẶT THAM SỐ ---
POINT_CLOUD_FILE_PATH = "1M_cloud.ply"

NORMAL_ESTIMATION_RADIUS_FACTOR = 1.0
NORMAL_ESTIMATION_MAX_NN = 30
ORIENT_NORMALS_K = 15

APPLY_ENHANCED_SHADING = True
SUN_DIRECTION = np.array([-0.6, -0.7, -1.0])
AMBIENT_STRENGTH = 0.15
DIFFUSE_STRENGTH = 0.85
SPECULAR_STRENGTH = 0.5
SHININESS_FACTOR = 50

INITIAL_POINT_SIZE = 2.0
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
INITIAL_BACKGROUND_IS_DARK = True
CAMERA_FIELD_OF_VIEW_DEG = 60

# --- BIẾN TOÀN CỤC CHO CALLBACKS ---
global_vis = None
global_pcd_display = None
global_pcd_original_colors = None
global_current_base_color_index = 0
global_bg_is_dark = INITIAL_BACKGROUND_IS_DARK
global_specular_on = True

DARK_BG_COLOR = np.array([0.08, 0.08, 0.08])
LIGHT_BG_COLOR = np.array([0.92, 0.92, 0.92])

BASE_COLORS_LIST = [
    ("Gray", np.array([0.7, 0.7, 0.7])),
    ("Steel Blue", np.array([0.4, 0.6, 0.8])),
    ("Pale Green", np.array([0.6, 0.8, 0.55])),
    ("Light Coral", np.array([0.9, 0.5, 0.5])),
    ("Original", None)
]

# --- HÀM TIỆN ÍCH ---
def load_point_cloud(filepath):
    global global_pcd_original_colors # Cần global để gán
    if not os.path.exists(filepath):
        print(f"Lỗi: File không tồn tại tại '{filepath}'")
        return None
    print(f"Đang tải point cloud từ: {filepath}...")
    _start_time = time.time()
    try:
        pcd = o3d.io.read_point_cloud(filepath)
        if not pcd.has_points():
            print("Lỗi: Point cloud rỗng sau khi tải.")
            return None
        
        if pcd.has_colors():
            global_pcd_original_colors = np.asarray(pcd.colors).copy()
            print("  Đã lưu màu gốc của point cloud.")
        else:
            global_pcd_original_colors = None
        
        _end_time = time.time()
        print(f"Tải thành công: {len(pcd.points)} điểm (trong {_end_time - _start_time:.2f}s).")
        return pcd
    except Exception as e:
        _end_time = time.time()
        print(f"Lỗi khi tải point cloud (sau {_end_time - _start_time:.2f}s): {e}")
        return None

def preprocess_point_cloud_for_shading(pcd, radius_factor, max_nn, orient_k):
    print("\n[Bước Tiền Xử Lý PCD]")
    _total_preprocess_time_start = time.time()

    if not pcd.has_normals():
        print("Point cloud chưa có pháp tuyến. Đang ước lượng...")
        _start_normals_time = time.time()
        if len(pcd.points) > max_nn:
            try:
                print("  Tính toán khoảng cách lân cận...")
                _start_dist_time = time.time()
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
                _end_dist_time = time.time()
                print(f"  Khoảng cách lân cận TB (ước lượng): {avg_dist:.4f}, Radius pháp tuyến: {radius:.4f} (tính trong {_end_dist_time - _start_dist_time:.2f}s)")
                if radius < 0.0001:
                    print(f"  Cảnh báo: Radius tính toán quá nhỏ ({radius:.6f}). Sử dụng fallback 0.005.")
                    radius = 0.005
            except Exception as e_dist:
                print(f"  Lỗi tính avg_dist: {e_dist}. Sử dụng radius mặc định (0.01).")
                radius = 0.01
        else:
            print(f"  PCD quá ít điểm. Sử dụng radius mặc định (0.01).")
            radius = 0.01
        
        _start_est_norm_time = time.time()
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
        _end_est_norm_time = time.time()
        print(f"  Ước lượng pháp tuyến cơ bản hoàn thành (trong {_end_est_norm_time - _start_est_norm_time:.2f}s).")

        _start_orient_norm_time = time.time()
        print("  Đang định hướng pháp tuyến...")
        pcd.orient_normals_consistent_tangent_plane(orient_k)
        _end_orient_norm_time = time.time()
        print(f"  Định hướng pháp tuyến hoàn thành (trong {_end_orient_norm_time - _start_orient_norm_time:.2f}s).")
        
        _end_normals_time = time.time()
        if not pcd.has_normals():
            print(f"  Ước lượng pháp tuyến thất bại (tổng thời gian: {_end_normals_time - _start_normals_time:.2f}s).")
        else:
            print(f"  Đã ước lượng và định hướng pháp tuyến (tổng thời gian: {_end_normals_time - _start_normals_time:.2f}s).")
    else:
        print("Point cloud đã có pháp tuyến (bỏ qua ước lượng).")

    if not pcd.has_colors():
        print("Point cloud chưa có màu gốc. Gán màu xám sáng mặc định làm màu cơ bản.")
        pcd.paint_uniform_color(BASE_COLORS_LIST[0][1])
    
    _total_preprocess_time_end = time.time()
    print(f"Hoàn thành tiền xử lý PCD (trong {_total_preprocess_time_end - _total_preprocess_time_start:.2f}s).")
    return pcd

def apply_enhanced_sun_shading(pcd_target, base_color_rgb_array,
                               sun_dir, view_pos,
                               ambient_s, diffuse_s, specular_s=0.0, shininess=32.0,
                               use_specular_flag=False):
    if not pcd_target.has_normals():
        print("Cảnh báo: Shading cần pháp tuyến.")
        pcd_target.paint_uniform_color(base_color_rgb_array if base_color_rgb_array is not None else [0.7,0.7,0.7])
        return pcd_target

    print(f"Đang áp dụng shading (Specular: {use_specular_flag})...")
    _start_shading_time = time.time()

    light_vector = -np.array(sun_dir) / np.linalg.norm(sun_dir)
    normals = np.asarray(pcd_target.normals)
    points = np.asarray(pcd_target.points)

    norm_lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    valid_normals_mask = norm_lengths.flatten() > 1e-9
    normals_normalized = np.zeros_like(normals)
    if np.any(valid_normals_mask):
        normals_normalized[valid_normals_mask] = normals[valid_normals_mask] / norm_lengths[valid_normals_mask]

    diffuse_intensity = np.sum(normals_normalized * light_vector, axis=1)
    diffuse_contrib = np.maximum(0, diffuse_intensity) * diffuse_s
    shaded_intensities = ambient_s + diffuse_contrib

    if use_specular_flag:
        view_vector_to_points = view_pos - points
        view_vector_norm = view_vector_to_points / (np.linalg.norm(view_vector_to_points, axis=1, keepdims=True) + 1e-9)
        half_vector = (light_vector + view_vector_norm)
        half_vector_norm = half_vector / (np.linalg.norm(half_vector, axis=1, keepdims=True) + 1e-9)
        spec_angle = np.sum(normals_normalized * half_vector_norm, axis=1)
        specular_contrib = specular_s * np.power(np.maximum(0, spec_angle), shininess)
        shaded_intensities += specular_contrib

    shaded_intensities = np.clip(shaded_intensities, 0, 1)

    if base_color_rgb_array is not None:
        if base_color_rgb_array.ndim == 1 and base_color_rgb_array.size == 3:
            base_colors_tiled = np.tile(base_color_rgb_array, (len(points), 1))
        elif base_color_rgb_array.ndim == 2 and base_color_rgb_array.shape[0] == len(points):
            base_colors_tiled = base_color_rgb_array
        else:
            print("Lỗi: base_color_rgb_array không hợp lệ. Dùng màu xám.")
            base_colors_tiled = np.tile(np.array([0.7,0.7,0.7]), (len(points),1))
        new_colors = base_colors_tiled * shaded_intensities[:, np.newaxis]
    else:
        print("Không có màu cơ bản hợp lệ, tạo màu xám dựa trên cường độ shading.")
        new_colors = np.tile(shaded_intensities[:, np.newaxis], (1, 3))

    pcd_target.colors = o3d.utility.Vector3dVector(np.clip(new_colors, 0, 1))
    
    _end_shading_time = time.time()
    print(f"Đã áp dụng shading (trong {_end_shading_time - _start_shading_time:.2f}s).")
    return pcd_target


# --- CALLBACKS CHO VISUALIZER ---
def toggle_background_color_cb(vis):
    # ... (Giữ nguyên) ...
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
    return False

def _refresh_shading(vis):
    # ... (Giữ nguyên) ...
    global global_pcd_display, global_specular_on, global_current_base_color_index, global_pcd_original_colors
    print("  Callback: Đang làm mới shading...")
    _start_refresh_time = time.time()
    color_name, color_rgb_data = BASE_COLORS_LIST[global_current_base_color_index]
    base_color_to_use = None
    if color_name == "Original" and global_pcd_original_colors is not None:
        base_color_to_use = global_pcd_original_colors
    else:
        base_color_to_use = color_rgb_data if color_rgb_data is not None else BASE_COLORS_LIST[0][1]
    view_control = vis.get_view_control()
    cam_params = view_control.convert_to_pinhole_camera_parameters()
    ext_inv = np.linalg.inv(cam_params.extrinsic)
    view_pos_current = ext_inv[:3, 3]
    apply_enhanced_sun_shading(global_pcd_display,
                               base_color_rgb_array=base_color_to_use,
                               sun_dir=SUN_DIRECTION, view_pos=view_pos_current,
                               ambient_s=AMBIENT_STRENGTH, diffuse_s=DIFFUSE_STRENGTH,
                               specular_s=SPECULAR_STRENGTH, shininess=SHININESS_FACTOR,
                               use_specular_flag=global_specular_on)
    vis.update_geometry(global_pcd_display)
    vis.poll_events() # Cần thiết để các thay đổi được áp dụng trước khi update_renderer
    vis.update_renderer()
    _end_refresh_time = time.time()
    print(f"  Callback: Hoàn thành làm mới shading (trong {_end_refresh_time - _start_refresh_time:.2f}s).")


def cycle_base_color_cb(vis):
    # ... (Giữ nguyên, _refresh_shading đã có timing) ...
    global global_pcd_display, global_current_base_color_index
    if global_pcd_display is None: return False
    global_current_base_color_index = (global_current_base_color_index + 1) % len(BASE_COLORS_LIST)
    color_name, _ = BASE_COLORS_LIST[global_current_base_color_index]
    print(f"Đổi màu cơ bản sang: {color_name}")
    if APPLY_ENHANCED_SHADING:
        _refresh_shading(vis)
    else:
        _start_color_change_time = time.time()
        color_name_new, color_rgb_data_new = BASE_COLORS_LIST[global_current_base_color_index]
        if color_name_new == "Original" and global_pcd_original_colors is not None:
            global_pcd_display.colors = o3d.utility.Vector3dVector(global_pcd_original_colors)
        elif color_rgb_data_new is not None:
            global_pcd_display.paint_uniform_color(color_rgb_data_new)
        else:
             global_pcd_display.paint_uniform_color(BASE_COLORS_LIST[0][1])
        vis.update_geometry(global_pcd_display)
        vis.poll_events()
        vis.update_renderer()
        _end_color_change_time = time.time()
        print(f"  Callback: Thay đổi màu cơ bản (không shading) hoàn thành (trong {_end_color_change_time - _start_color_change_time:.2f}s).")
    return False

def toggle_specular_cb(vis):
    # ... (Giữ nguyên, _refresh_shading đã có timing) ...
    global global_specular_on, global_pcd_display
    if global_pcd_display is None or not APPLY_ENHANCED_SHADING:
        print("Specular toggle chỉ hoạt động khi APPLY_ENHANCED_SHADING là True.")
        return False
    global_specular_on = not global_specular_on
    print(f"Specular shading {'BẬT' if global_specular_on else 'TẮT'}.")
    _refresh_shading(vis)
    return False

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    overall_start_time = time.time()
    print("--- Point Cloud Renderer with Timing & Customization ---")

    pcd_original_loaded = load_point_cloud(POINT_CLOUD_FILE_PATH)
    if pcd_original_loaded is None:
        exit()

    # Tạo bản sao để xử lý
    pcd_processed = o3d.geometry.PointCloud(pcd_original_loaded)
    pcd_processed = preprocess_point_cloud_for_shading(pcd_processed,
                                                       radius_factor=NORMAL_ESTIMATION_RADIUS_FACTOR,
                                                       max_nn=NORMAL_ESTIMATION_MAX_NN,
                                                       orient_k=ORIENT_NORMALS_K)
    
    global_pcd_display = o3d.geometry.PointCloud(pcd_processed) # Gán cho biến toàn cục

    if APPLY_ENHANCED_SHADING:
        print("\n[Bước Áp Dụng Shading Ban Đầu]")
        # Ước lượng view_pos ban đầu cho shading
        bbox = global_pcd_display.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent_max = np.max(bbox.get_extent())
        if extent_max < 1e-6 : extent_max = 1.0
        initial_view_pos_est = center + np.array([0.0, 0.0, extent_max * 2.5])

        base_color_to_use = None
        color_name_init, color_rgb_data_init = BASE_COLORS_LIST[global_current_base_color_index]
        if color_name_init == "Original" and global_pcd_original_colors is not None:
            base_color_to_use = global_pcd_original_colors
        else:
            base_color_to_use = color_rgb_data_init if color_rgb_data_init is not None else BASE_COLORS_LIST[0][1]

        apply_enhanced_sun_shading(global_pcd_display,
                                   base_color_rgb_array=base_color_to_use,
                                   sun_dir=SUN_DIRECTION,
                                   view_pos=initial_view_pos_est,
                                   ambient_s=AMBIENT_STRENGTH,
                                   diffuse_s=DIFFUSE_STRENGTH,
                                   specular_s=SPECULAR_STRENGTH,
                                   shininess=SHININESS_FACTOR,
                                   use_specular_flag=global_specular_on)
    # else:
    # (Phần gán màu ban đầu nếu không shading có thể bỏ qua vì preprocess đã gán màu mặc định)

    geometries_to_draw = [global_pcd_display]

    print("\n--- KHỞI ĐỘNG OPEN3D VISUALIZER ---")
    # ... (Hướng dẫn phím bấm giữ nguyên) ...
    print("  - Phím 'L': Chuyển đổi giữa các chế độ chiếu sáng. **TÌM CHẾ ĐỘ EDL**.")
    print("  - Phím 'B': Đổi màu nền (Sáng/Tối).")
    print("  - Phím 'X': Duyệt qua các màu cơ bản của Point Cloud.")
    print("  - Phím 'K': Bật/Tắt hiệu ứng Specular (nếu Shading thủ công được bật).")
    print("  - Phím 'P' / '+': Tăng kích thước điểm.  'M' / '-': Giảm kích thước điểm.")
    print("  - Kéo chuột trái: Xoay camera.")
    print("  - Lăn chuột: Zoom.")
    print("  - Kéo chuột phải / Shift + Kéo chuột trái: Di chuyển camera (Pan).")
    print("  - Phím 'S': Chuyển đổi giữa các kiểu tô bóng.")
    print("  - Phím 'N': Bật/tắt hiển thị pháp tuyến (vector).")
    print("  - Phím 'C': In thông số camera ra console.")
    print("  - Ctrl + Left Click vào điểm: In thông tin điểm ra console.")
    print("  - Phím 'R': Reset view về mặc định.")
    print("  - Phím 'Q' hoặc đóng cửa sổ: Thoát.")


    global_vis = o3d.visualization.VisualizerWithKeyCallback()
    global_vis.create_window(window_name="Interactive Point Cloud Renderer (Timed)",
                             width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    for geom in geometries_to_draw:
        global_vis.add_geometry(geom)
    
    render_option = global_vis.get_render_option()
    if INITIAL_BACKGROUND_IS_DARK:
        render_option.background_color = DARK_BG_COLOR
    else:
        render_option.background_color = LIGHT_BG_COLOR
        global_bg_is_dark = False

    render_option.point_size = INITIAL_POINT_SIZE
    render_option.light_on = False

    global_vis.register_key_callback(ord('B'), toggle_background_color_cb)
    global_vis.register_key_callback(ord('X'), cycle_base_color_cb)
    global_vis.register_key_callback(ord('K'), toggle_specular_cb)

    # --- Thiết lập Camera Parameters ---
    print("\n[Bước Thiết Lập Camera Ban Đầu]")
    _start_cam_setup_time = time.time()
    view_control = global_vis.get_view_control()
    fov_rad = np.deg2rad(CAMERA_FIELD_OF_VIEW_DEG)
    fy = WINDOW_HEIGHT / (2 * np.tan(fov_rad / 2.0))
    fx = fy
    cx = WINDOW_WIDTH / 2.0
    cy = WINDOW_HEIGHT / 2.0
    new_intrinsic = o3d.camera.PinholeCameraIntrinsic(WINDOW_WIDTH, WINDOW_HEIGHT, fx, fy, cx, cy)
    
    global_vis.poll_events() # Quan trọng để visualizer kịp cập nhật
    global_vis.update_renderer() # và tính toán extrinsic ban đầu

    current_pinhole_params = view_control.convert_to_pinhole_camera_parameters()
    current_extrinsic = current_pinhole_params.extrinsic
    
    new_cam_params = o3d.camera.PinholeCameraParameters()
    new_cam_params.intrinsic = new_intrinsic
    new_cam_params.extrinsic = current_extrinsic
    view_control.convert_from_pinhole_camera_parameters(new_cam_params, allow_arbitrary=True)
    _end_cam_setup_time = time.time()
    print(f"  Đã cố gắng đặt Field of View ~{CAMERA_FIELD_OF_VIEW_DEG} độ (trong {_end_cam_setup_time - _start_cam_setup_time:.2f}s).")

    overall_setup_time = time.time() - overall_start_time
    print(f"\nTổng thời gian chuẩn bị trước khi chạy Visualizer: {overall_setup_time:.2f}s")
    print("\nVisualizer đang chạy. Hãy thử các phím điều khiển (B, L, X, K, P, M,...).")
    
    global_vis.run() # Hàm này block
    
    print("\nCửa sổ Visualizer đã đóng.")
    global_vis.destroy_window()
    global_vis = None

    overall_end_time = time.time()
    print(f"\n--- Kết thúc hiển thị (Tổng thời gian chạy script: {overall_end_time - overall_start_time:.2f}s) ---")