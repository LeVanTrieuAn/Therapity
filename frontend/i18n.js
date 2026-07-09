/* i18n.js — Thapsang Internationalization Engine v2 */
/* Supports: vi (Tiếng Việt), en (English)            */
/* Syncs across all pages via localStorage             */

(function () {
    const LANG_KEY = 'thapsang_lang';
    window.currentLang = localStorage.getItem(LANG_KEY) || 'vi';

    const THEME_KEY = 'thapsang_theme';
    window.currentTheme = localStorage.getItem(THEME_KEY) || localStorage.getItem('theme') || 'dark';

    // Apply theme class immediately to avoid layout flash
    const isDark = window.currentTheme === 'dark';
    document.documentElement.classList.toggle('dark', isDark);
    document.documentElement.classList.toggle('light', !isDark);

    /* ── Sidebar Toggle Logic (Mini-Sidebar) ── */
    let tsMainWrapper = null;

    const sidebarStyle = document.createElement('style');
    sidebarStyle.innerHTML = `
        aside.fixed.left-0 {
            transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), padding 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow-x: hidden;
            white-space: nowrap; /* Prevent all text wrapping during width transitions */
        }
        main, .ts-main-wrapper, #ts-main-wrapper, .md\\:ml-64 {
            transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        aside.sidebar-collapsed {
            width: 5.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        @media (min-width: 768px) {
            .main-collapsed {
                margin-left: 5.5rem !important;
            }
        }

        /* Hide Logo visually but preserve its exact natural height to prevent shifting */
        /* aside.sidebar-collapsed > div.mb-12 > div.flex > div:first-child */,
        /* aside.sidebar-collapsed > div.mb-12 > div.flex > div:first-child */ * {
            visibility: hidden !important;
            opacity: 0 !important;
            white-space: nowrap !important;
        }
        /* aside.sidebar-collapsed > div.mb-12 > div.flex > div:first-child */ {
            width: 0 !important;
            overflow: hidden !important;
        }

        /* Allow controls container to position the arrow */
        /* aside.sidebar-collapsed > div.mb-12 > div.flex > div.flex.items-center { */
            display: block !important;
        }

        /* Hide Theme & Language toggles when closed */
        aside.sidebar-collapsed #ts-theme-btn,
        aside.sidebar-collapsed .ts-lang-dropdown {
            display: none !important;
        }

        /* Adjust Navigation Links */
        /* Let flexbox handle alignment naturally to prevent horizontal jumping */
        aside.sidebar-collapsed .flex-grow > a > span:nth-child(2) {
            display: none !important;
        }

        /* Adjust User Panel */
        /* Lock inner containers to exactly 40px so the avatar never shifts relative to the box */
        aside .mt-auto .group,
        aside .mt-auto .group > div.flex-col {
            height: 40px !important;
            justify-content: center !important;
        }
        /* Apply alignment shift ONLY in expanded state */
        aside:not(.sidebar-collapsed) .mt-auto .group {
            transform: translateX(-8px) !important;
        }
        /* Pull the text left to counteract the 12px gap, making it perfectly align with module text */
        aside:not(.sidebar-collapsed) .mt-auto .group > div.flex-col {
            margin-left: -8px !important;
        }
        
        /* Ensure it is perfectly centered in the gray box in collapsed state */
        aside.sidebar-collapsed .mt-auto .group {
            transform: none !important;
            margin-left: 0 !important;
            justify-content: center !important;
        }
        /* Let flexbox handle alignment naturally to prevent horizontal jumping */
        aside.sidebar-collapsed .mt-auto .group > div.flex-col {
            display: none !important;
        }

        /* Hide App Version without altering layout height */
        aside.sidebar-collapsed .app-version-badge {
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        /* Adjust Toggle Button & Add Rotation */
        #ts-sidebar-toggle {
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), left 0.4s cubic-bezier(0.4, 0, 0.2, 1), right 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        aside.sidebar-collapsed #ts-sidebar-toggle {
            right: auto !important;
            left: -28px !important;
            transform: translateX(-50%) rotate(180deg) !important;
        }
    `;
    document.head.appendChild(sidebarStyle);

    window.toggleSidebar = function () {
        let sidebar = document.querySelector('aside');
        const main = tsMainWrapper || document.querySelector('.md\\:ml-64') || document.querySelector('main');

        if (!sidebar) return;

        const isClosed = sidebar.classList.contains('sidebar-collapsed');

        if (isClosed) {
            // Open (Expand)
            sidebar.classList.remove('sidebar-collapsed');
            if (main) main.classList.remove('main-collapsed');
            localStorage.setItem('thapsang_sidebar_closed', 'false');
        } else {
            // Close (Collapse)
            sidebar.classList.add('sidebar-collapsed');
            if (main) main.classList.add('main-collapsed');
            localStorage.setItem('thapsang_sidebar_closed', 'true');
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        tsMainWrapper = document.querySelector('.md\\:ml-64') || document.querySelector('main');

        if (localStorage.getItem('thapsang_sidebar_closed') === 'true') {
            let sidebar = document.querySelector('aside');

            if (sidebar) {
                // Disable transition for initial load
                sidebar.style.transition = 'none';
                if (tsMainWrapper) tsMainWrapper.style.transition = 'none';

                sidebar.classList.add('sidebar-collapsed');
                if (tsMainWrapper) tsMainWrapper.classList.add('main-collapsed');

                // Re-enable transition after a short delay
                setTimeout(() => {
                    sidebar.style.transition = '';
                    if (tsMainWrapper) tsMainWrapper.style.transition = '';
                }, 50);
            }
        }
    });

    /* ══════════════════════════════════════════════════════
       TRANSLATION DICTIONARY
    ══════════════════════════════════════════════════════ */
    const translations = {
        vi: {
            /* ── Sidebar navigation ── */
            'nav.coach': 'Tham vấn',
            'nav.diary': 'Nhật ký',
            'nav.aoa': 'Bản tin AOA',
            'nav.tasks': 'Nhiệm vụ',
            'nav.analytics': 'Thống kê',
            'nav.cohort': 'Lộ trình cá nhân',
            'nav.personal_roadmap': 'Lộ trình cá nhân',

            /* ── Sidebar footer ── */
            'sidebar.tagline': 'Mindset OS',
            'sidebar.logout': 'Đăng xuất',
            'common.switch_theme': 'Chuyển giao diện',

            /* ── Settings panel ── */
            'settings.title': 'Cài đặt',
            'settings.language': 'Ngôn ngữ',

            /* ══ LOGIN PAGE ══════════════════════════════ */
            'login.tab_login': 'Đăng nhập',
            'login.tab_register': 'Đăng ký',
            'login.email': 'Email',
            'login.email_ph': 'Nhập email...',
            'login.email_example': 'example@email.com',
            'login.password': 'Mật khẩu',
            'login.remember': 'Ghi nhớ',
            'login.forgot_pwd': 'Quên mật khẩu?',
            'login.btn_login': 'Đăng nhập',
            'login.fullname': 'Họ và tên',
            'login.fullname_ph': 'Nhập họ và tên...',
            'login.confirm_password': 'Xác nhận mật khẩu',
            'login.btn_register': 'Tạo tài khoản',
            'login.otp_title': 'Xác nhận OTP',
            'login.otp_desc': 'Vui lòng nhập mã 6 ký tự đã được gửi đến email',
            'login.otp_label': 'Mã OTP',
            'login.btn_otp': 'Xác nhận & Đăng nhập',
            'login.forgot_title': 'Khôi phục mật khẩu',
            'login.forgot_desc': 'Nhập email bạn đã đăng ký để nhận mã khôi phục.',
            'login.btn_send_otp': 'Gửi mã xác nhận',
            'login.confirm_otp_title': 'Xác nhận mã',
            'login.confirm_otp_desc': 'Vui lòng nhập mã 6 ký tự đã gửi đến',
            'login.btn_continue': 'Tiếp tục',
            'login.new_pwd_title': 'Tạo mật khẩu mới',
            'login.new_pwd_label': 'Mật khẩu mới',
            'login.btn_reset_pwd': 'Đổi mật khẩu',
            'login.msg_recovery_sent': 'Đã gửi mã khôi phục tới email của bạn!',
            'login.msg_sys_error': 'Lỗi hệ thống',
            'login.msg_conn_error': 'Không thể kết nối tới máy chủ',
            'login.msg_otp_valid': 'Mã hợp lệ, mời bạn tạo mật khẩu mới.',
            'login.msg_pwd_mismatch': 'Mật khẩu xác nhận không khớp!',
            'login.msg_pwd_changed': 'Đổi mật khẩu thành công! Mời bạn đăng nhập.',
            'login.msg_otp_sent': 'Mã OTP đã được gửi! Vui lòng kiểm tra email.',
            'login.msg_required': 'Vui lòng điền vào trường này.',
            'login.msg_email_invalid': 'Vui lòng nhập địa chỉ email hợp lệ.',
            /* Backend Errors */
            'Sai thông tin đăng nhập': 'Sai thông tin đăng nhập',
            'Tài khoản đã tồn tại': 'Tài khoản đã tồn tại',
            'Mã OTP không hợp lệ hoặc đã hết hạn': 'Mã OTP không hợp lệ hoặc đã hết hạn',
            'Email không tồn tại trong hệ thống': 'Email không tồn tại trong hệ thống',
            'Không tìm thấy tài khoản': 'Không tìm thấy tài khoản',
            'Số lần nhập sai đã hơn 5 lần, vui lòng thử lại sau.': 'Số lần nhập sai đã hơn 5 lần, vui lòng thử lại sau.',
            'Mật khẩu mới phải khác với 3 mật khẩu gần đây nhất.': 'Mật khẩu mới phải khác với 3 mật khẩu gần đây nhất.',
            'Mật khẩu phải bao gồm cả chữ và số.': 'Mật khẩu phải bao gồm cả chữ và số.',
            'Mật khẩu không hợp lệ theo quy tắc của hệ thống.': 'Mật khẩu không hợp lệ theo quy tắc của hệ thống.',

            /* ══ ONBOARDING PAGE ════════════════════════════ */
            'ob.welcome': 'Chào mừng bạn',
            'ob.tagline': 'Mindset OS',
            'ob.q_dob': 'Ngày sinh của bạn?',
            'ob.sub_dob': 'Giúp chúng tôi cá nhân hóa trải nghiệm cho bạn',
            'ob.day': 'Ngày',
            'ob.month': 'Tháng',
            'ob.year': 'Năm',
            'ob.q_gender': 'Giới tính của bạn?',
            'ob.sub_gender': 'Thông tin này hoàn toàn bảo mật',
            'ob.q_interests': 'Sở thích của bạn?',
            'ob.sub_interests': 'Chọn tất cả những gì phù hợp với bạn',
            'ob.q_problems': 'Bạn đang gặp vấn đề gì?',
            'ob.sub_problems': 'Coach AI sẽ giúp bạn giải quyết những vấn đề này',
            'ob.q_goals': 'Mục tiêu sử dụng ứng dụng?',
            'ob.sub_goals': 'Chúng tôi sẽ tối ưu trải nghiệm theo mục tiêu của bạn',
            'ob.q_source': 'Bạn biết đến Thapsang qua đâu?',
            'ob.sub_source': 'Giúp chúng tôi cải thiện trải nghiệm tiếp cận',
            'ob.btn_back': 'Quay lại',
            'ob.btn_next': 'Tiếp theo',
            'ob.btn_start': 'Bắt đầu hành trình',
            'ob.btn_saving': 'Đang lưu...',
            'ob.btn_skip': 'Bỏ qua, tôi sẽ khám phá sau →',

            /* Onboarding Options */
            'Nam': 'Nam', 'Nữ': 'Nữ', 'Khác': 'Khác', 'Không muốn tiết lộ': 'Không muốn tiết lộ',
            'Đọc sách': 'Đọc sách', 'Thể thao': 'Thể thao', 'Âm nhạc': 'Âm nhạc', 'Du lịch': 'Du lịch', 'Công nghệ': 'Công nghệ', 'Nghệ thuật': 'Nghệ thuật', 'Nấu ăn': 'Nấu ăn', 'Thiền & Yoga': 'Thiền & Yoga', 'Viết lách': 'Viết lách', 'Phim ảnh': 'Phim ảnh',
            'Căng thẳng / Stress': 'Căng thẳng / Stress', 'Mất tập trung': 'Mất tập trung', 'Thiếu động lực': 'Thiếu động lực', 'Mất ngủ': 'Mất ngủ', 'Lo âu': 'Lo âu', 'Khó kiểm soát cảm xúc': 'Khó kiểm soát cảm xúc', 'Thiếu mục tiêu sống': 'Thiếu mục tiêu sống', 'Cô đơn': 'Cô đơn', 'Trì hoãn': 'Trì hoãn', 'Tự ti': 'Tự ti',
            'Quản lý cảm xúc': 'Quản lý cảm xúc', 'Phát triển bản thân': 'Phát triển bản thân', 'Tăng năng suất': 'Tăng năng suất', 'Cải thiện giấc ngủ': 'Cải thiện giấc ngủ', 'Xây dựng thói quen tốt': 'Xây dựng thói quen tốt', 'Tìm hiểu bản thân': 'Tìm hiểu bản thân', 'Kết nối cộng đồng': 'Kết nối cộng đồng', 'Giảm căng thẳng': 'Giảm căng thẳng',
            'Bạn bè giới thiệu': 'Bạn bè giới thiệu', 'Mạng xã hội': 'Mạng xã hội', 'Tìm kiếm Google': 'Tìm kiếm Google', 'Báo chí / Truyền thông': 'Báo chí / Truyền thông', 'Trường học / Công ty': 'Trường học / Công ty',

            /* ══ COACH PAGE ══════════════════════════════ */
            'coach.title': 'Đối thoại Socratic',
            'coach.subtitle': 'Lọc bỏ tiếng ồn. Tìm lại cốt lõi.',
            'coach.welcome_prefix': 'Chào mừng ',
            'coach.welcome_suffix': '. Hãy chia sẻ điều gì đang khiến bạn bận tâm?',
            'coach.history': 'Lịch sử',
            'coach.sessions': 'Phiên thảo luận',
            'coach.no_history': 'Chưa có lịch sử',
            'coach.post': 'Đăng bài',
            'coach.topography': 'Sơ đồ tư duy',
            'coach.no_mindmap_data': '',
            'coach.new_task': 'Nhiệm vụ\nmới',
            'coach.tasks': 'Nhiệm vụ',
            'coach.placeholder': 'Nhập suy nghĩ của bạn...',
            'coach.thinking': 'Luồng suy nghĩ nội tâm',
            'coach.center_map': 'Căn giữa bản đồ',
            'coach.regenerate': 'Thử lại',
            'coach.play_voice': 'Phát giọng nói',
            'coach.diary_consent_prompt': 'Chúng tôi đã nhận thấy đủ dữ liệu để ghi lại những gì bạn đã chia sẻ, bạn có muốn AI tạo và cập nhật ghi chép ở phần Nhật Ký không?',
            'coach.diary_consent_always': 'Luôn đồng ý tự động ghi nhật ký (bỏ qua câu hỏi này cho các lần sau)',
            'coach.diary_consent_decline': 'Từ chối',
            'coach.diary_consent_accept': 'Đồng ý',
            'coach.diary_consent_toast': 'Đã yêu cầu AI tạo nhật ký ở chế độ nền...',

            /* ══ DIARY PAGE ══════════════════════════════ */
            'diary.vault': 'Vùng Thapsang',
            'diary.draft': 'Soạn thảo',
            'diary.preview': 'Xem trước',
            'diary.root_files': 'File gốc',
            'diary.search': 'Tìm kiếm tài liệu',
            'diary.mirror': 'Gương phản tỉnh',
            'diary.synced': 'Đã đồng bộ',
            'diary.syncing': 'Đang đồng bộ',
            'diary.new_note': 'Tạo note mới',
            'diary.graph_desc': 'Sơ đồ mô tả trực quan mối liên kết giữa các ghi chép và thư mục của bạn. Bấm vào nút tròn để mở nhanh ghi chép đó.',
            'diary.words': 'từ',
            'diary.chars': 'ký tự',
            'diary.today': 'Hôm nay',
            'diary.ai_reflecting': 'AI đang soi gương',
            'diary.save': 'Lưu',
            'diary.title_ph': 'Tiêu đề nhật ký',
            'diary.content_ph': 'Bắt đầu gõ những dòng suy nghĩ sâu sắc của bạn tại đây...',
            'diary.new_folder': 'Tạo thư mục mới',
            'diary.sort': 'Sắp xếp',
            'diary.sort_newest': 'Mới nhất',
            'diary.sort_oldest': 'Cũ nhất',
            'diary.sort_alpha': 'Tên A - Z',
            'diary.delete_folder': 'Xóa thư mục này',
            'diary.focus_mode': 'Focus Mode',
            'diary.exit_focus_mode': 'Thoát Focus Mode',
            'diary.close_panel': 'Đóng panel',
            'diary.building_graph': 'Đang dựng sơ đồ liên kết',
            'diary.untitled': 'Không có tiêu đề',
            'diary.modal_label': 'Tên gọi / Tiêu đề',
            'diary.cancel': 'Hủy',
            'diary.create_btn': 'Tạo ngay',
            'diary.confirm_delete': 'Xác nhận xóa',
            'diary.create_note_title': 'Tạo ghi chép mới',
            'diary.create_note_ph': 'Nhập tiêu đề ghi chép',
            'diary.create_folder_title': 'Tạo thư mục mới',
            'diary.create_folder_ph': 'Nhập tên thư mục',
            'diary.delete_note_title': 'Xác nhận xóa ghi chép',
            'diary.delete_note_msg': 'Bạn có chắc chắn muốn xóa ghi chép "{title}" vĩnh viễn không? Thao tác này không thể hoàn tác.',
            'diary.delete_folder_title': 'Xác nhận xóa thư mục',
            'diary.delete_folder_msg_with_notes': 'Thư mục "{folder}" đang chứa {count} ghi chép. Xóa thư mục này sẽ xóa VĨNH VIỄN toàn bộ thư mục và các ghi chép bên trong. Bạn có chắc chắn muốn tiếp tục?',
            'diary.delete_folder_msg_empty': 'Bạn có chắc chắn muốn xóa thư mục trống "{folder}" không?',
            'diary.toast_load_err': 'Không thể tải nhật ký từ máy chủ.',
            'diary.toast_sort_info': 'Đã sắp xếp danh sách tài liệu.',
            'diary.toast_create_note_ok': 'Đã tạo ghi chép mới thành công!',
            'diary.toast_create_note_fail': 'Lưu ghi chép mới thất bại.',
            'diary.toast_folder_exists': 'Thư mục đã tồn tại.',
            'diary.toast_create_folder_ok': 'Đã tạo thư mục "{folder}" thành công!',
            'diary.toast_create_folder_fail': 'Tạo thư mục mới thất bại.',
            'diary.toast_ai_reflecting': 'AI tham vấn đang tiếp nhận thông tin...',
            'diary.toast_save_ok': 'Ghi chép đã tiếp nhận',
            'diary.toast_save_fail': 'Lưu ghi chép thất bại.',
            'diary.toast_deleting_note': 'Đang xóa ghi chép...',
            'diary.toast_delete_draft_ok': 'Đã xóa note nháp.',
            'diary.toast_delete_note_ok': 'Đã xóa ghi chép thành công.',
            'diary.toast_delete_note_fail': 'Xóa ghi chép thất bại.',
            'diary.toast_deleting_folder': 'Đang xóa thư mục...',
            'diary.toast_delete_folder_ok': 'Đã xóa thư mục "{folder}" thành công!',
            'diary.toast_delete_folder_fail': 'Không thể xóa thư mục hoàn toàn.',
            'diary.toast_auto_creating': 'Đang tự động tạo ghi chép "{title}"...',
            'diary.toast_auto_create_ok': 'Đã liên kết & tạo ghi chép "{title}" thành công!',
            'diary.toast_auto_create_fail': 'Tự động tạo ghi chép thất bại.',
            'diary.import_files': 'Nhập File',
            'diary.import_folder': 'Nhập Thư mục',
            'diary.export': 'Xuất tài liệu',

            /* ══ AOA FEED PAGE ═══════════════════════════ */
            'aoa.title': 'Hỏi mọi người bất cứ điều gì',
            'aoa.community': 'Cộng đồng',
            'aoa.trending': 'Xu hướng',
            'aoa.profile': 'Trang cá nhân',
            'aoa.search': 'Tìm kiếm bài viết...',
            'aoa.new_post': 'Bài viết mới',
            'aoa.share_mind': 'Chia sẻ suy nghĩ của bạn...',
            'aoa.publish': 'Đăng',
            'aoa.following': 'Đang theo dõi',
            'aoa.follow': 'Theo dõi',
            'aoa.no_posts': 'Chưa có bài đăng nào.',
            'aoa.content_mgmt': 'Quản lý nội dung',
            'aoa.hidden_posts': 'Bài viết đã ẩn',
            'aoa.hidden_posts_desc': 'Các bài viết bạn không muốn thấy',
            'aoa.deleted_posts': 'Bài viết đã xóa',
            'aoa.deleted_posts_desc': 'Thùng rác của bạn',
            'aoa.hidden_title': 'Những bài viết đã ẩn',
            'aoa.deleted_title': 'Những bài viết đã xóa',
            'aoa.hidden_title_desc': 'Danh sách các bài viết đã được lưu trữ riêng',
            'aoa.deleted_title_desc': 'Bài viết sẽ tự động xóa sau 30 ngày',
            'aoa.back': 'Quay lại',
            'aoa.no_more_posts': 'Bạn đã xem hết bài viết',
            'aoa.privacy_public': 'Công khai',
            'aoa.privacy_followers': 'Chỉ cho người theo dõi',
            'aoa.privacy_private': 'Riêng tư',

            /* -- AOA Added translation keys -- */
            'aoa.ai_report_title': 'Xu hướng hiện nay',
            'aoa.compiling_community': 'Đang tổng hợp dữ liệu cộng đồng...',
            'aoa.analysis_posts': 'Bài đăng phân tích',
            'aoa.interactions': 'Lượt tương tác',
            'aoa.trending_posts': 'Nội dung đang gây bão',
            'aoa.loading_pathway': 'Đang tải lịch trình...',
            'aoa.loading_more': 'Đang tải thêm...',
            'aoa.coach_suggestions': 'Gợi ý Coach',
            'aoa.sort_by': 'Sắp xếp theo:',
            'aoa.influence': 'Tầm ảnh hưởng',
            'aoa.followers': 'Số người theo dõi',
            'aoa.name_az': 'Tên (A-Z)',
            'aoa.followers_count': 'người theo dõi',
            'aoa.ask_ai_coach': 'Hỏi AI Coach',
            'aoa.send_message': 'Nhắn tin',
            'aoa.view_mindmap': 'Xem Mindmap',
            'aoa.explore_experts_link': 'Khám phá thêm chuyên gia',
            'aoa.explore_experts_title': 'Khám phá Chuyên gia Thapsang',
            'aoa.explore_experts_desc': 'Tìm kiếm và theo dõi các Chuyên gia AI & hỗ trợ tư duy xuất sắc nhất.',
            'aoa.explore_search_ph': 'Tìm kiếm chuyên gia theo tên, mô tả hoặc từ khóa...',
            'aoa.tag_all': 'Tất cả',
            'aoa.tag_ai_mentor': 'Chuyên gia AI',
            'aoa.tag_expert': 'Chuyên gia',
            'aoa.tag_mindset': 'Mindset',
            'aoa.tag_psychology': 'Tâm lý',
            'aoa.ai_analyzing_mindset': 'AI đang phân tích tư duy...',
            'aoa.mindmap_title': 'Sơ đồ tư duy',
            'aoa.ai_live_scan': 'AI Live Scan',
            'aoa.behavioral_analysis': 'Phân tích hành vi',
            'aoa.not_enough_data_keywords': 'Chưa có đủ dữ liệu để phân tích',
            'aoa.ai_analyzing_data': 'AI đang phân tích dữ liệu của bạn...',
            'aoa.mbti_classification': 'Phân loại tính cách MBTI',
            'aoa.mbti_not_enough_data': 'AI chưa đủ dữ liệu để phân loại MBTI. Hãy chia sẻ thêm nhé!',
            'aoa.dim_objective': 'Khách quan',
            'aoa.dim_emotion': 'Cảm xúc',
            'aoa.dim_negative': 'Tiêu cực',
            'aoa.dim_positive': 'Tích cực',
            'aoa.dim_creativity': 'Sáng tạo',
            'aoa.dim_overview': 'Tổng quan',
            'aoa.tag_strategy': 'Chiến lược',
            'aoa.core_expertise': 'Chuyên môn chính: ',
            'aoa.no_experts_found': 'Không tìm thấy chuyên gia nào phù hợp',
            'aoa.edit_profile': 'Chỉnh sửa hồ sơ',
            'aoa.profile_settings': 'Thiết lập hồ sơ',
            'aoa.cancel': 'Hủy',
            'aoa.save_changes': 'Lưu thay đổi',
            'aoa.display_name': 'Tên hiển thị',
            'aoa.display_name_tip': 'Mẹo: Tên hiển thị giúp mọi người dễ nhận diện bạn hơn.',
            'aoa.account_id_static': 'Account ID (Tĩnh)',
            'aoa.account_id_tip': 'ID này được cố định để bảo toàn lịch sử bài viết của bạn.',
            'aoa.bio_label': 'Giới thiệu bản thân',
            'aoa.default_bio': 'Học hỏi, chia sẻ và cùng nhau phát triển tại cộng đồng Thapsang. Đam mê tri thức và sự sáng tạo.',
            'aoa.my_posts': 'Bài đăng của tôi',
            'aoa.posts': 'Bài đăng',
            'aoa.mindset_metrics': 'Chỉ số tư duy',
            'aoa.mind_map': 'Sơ đồ tư duy',
            'aoa.ai_live_scan': 'AI cập nhật trực tiếp',
            'aoa.zoom_mindmap': 'Phóng to sơ đồ tư duy',
            'aoa.behavioral_analysis': 'Phân tích hành vi',
            'aoa.insufficient_data': 'Chưa có đủ dữ liệu để phân tích',
            'aoa.mbti_classification': 'Phân loại tính cách MBTI',
            'aoa.mbti_insufficient_data': 'AI chưa đủ dữ liệu để phân loại MBTI. Hãy chia sẻ thêm nhé!',
            'aoa.close': 'Đóng',
            'aoa.ai_mindset_map': 'Sơ đồ tư duy AI',
            'aoa.tactical_display': 'Chế độ phân tích chi tiết',
            'aoa.interactive_map_desc': 'Bản đồ tư duy tương tác chuẩn xác dựa trên dữ liệu thời gian thực.',
            'aoa.zoom_mindmap': 'Phóng to sơ đồ tư duy',
            'aoa.detailed_analysis_mode': 'Chế độ phân tích chi tiết',
            'aoa.interactive_mindmap_realtime': 'Bản đồ tư duy tương tác chuẩn xác dựa trên dữ liệu thời gian thực.',
            'aoa.ai_analyzing_mindset': 'AI đang phân tích tư duy...',
            'aoa.add_comment_ph': 'Thêm nhận xét của bạn...',
            'aoa.comment_ph': 'Nhận xét...',
            'aoa.share_post_title': 'Chia sẻ bài viết',
            'aoa.repost_comment_ph': 'Thêm nhận xét của bạn...',
            'aoa.sharing_thoughts': 'Chia sẻ suy nghĩ...',
            'aoa.shared_success_title': 'Đã chia sẻ!',
            'aoa.shared_success_desc': 'Bài viết đã được đăng lại thành công vào mục Bài đăng của tôi.',
            'aoa.awesome': 'Tuyệt vời',
            'aoa.hide_post': 'Ẩn bài viết',
            'aoa.unhide_post': 'Hủy ẩn bài viết',
            'aoa.unhide_post_msg': 'Bài viết sẽ quay trở lại bảng tin cộng đồng.',
            'aoa.hide_post_msg': 'Bạn sẽ không thấy bài viết này trên bảng tin nữa.',
            'aoa.save_post': 'Lưu bài viết',
            'aoa.unsave_post': 'Hủy lưu bài viết',
            'aoa.report_post': 'Báo cáo',
            'aoa.restore_post': 'Khôi phục bài viết',
            'aoa.edit_post': 'Sửa bài viết',
            'aoa.delete_post': 'Xóa bài viết',
            'aoa.thank_you': 'Cảm ơn',
            'aoa.report_received': 'Chúng tôi đã ghi nhận báo cáo của bạn.',
            'aoa.delete_permanent': 'Xóa vĩnh viễn',
            'aoa.delete_confirm': 'Xác nhận xóa',
            'aoa.delete_permanent_msg': 'Hành động này sẽ xóa bài viết hoàn toàn khỏi hệ thống.',
            'aoa.delete_confirm_msg': 'Bài viết sẽ được chuyển vào mục \'Bài viết đã xóa\'.',
            'aoa.restored_title': 'Đã khôi phục',
            'aoa.restored_msg': 'Bài viết đã được đưa trở lại bảng tin chính.',
            'aoa.success_sync': 'Hồ sơ của bạn đã được cập nhật thành công!',
            'aoa.error_sync': 'Không thể đồng bộ lên máy chủ. Vui lòng kiểm tra kết nối và thử lại.',
            'aoa.post_by': 'Bài viết của',
            'aoa.original_post': 'Bài gốc:',
            'aoa.reposted': 'đã đăng lại',
            'aoa.likes_label': 'Lượt thích',
            'aoa.followers_label': 'Người theo dõi',
            'aoa.following_label': 'Đang theo dõi',
            'aoa.mbti_tip': 'Dựa trên thói quen làm việc và tương tác',
            'aoa.trending_label': 'Thịnh hành',
            'aoa.viral_content': 'Nội dung đang gây bão',
            'aoa.based_on_community': 'Dựa trên phân tích nội dung cộng đồng',
            'aoa.engagement_score': 'điểm tương tác',

            'dims.objective': 'Khách quan',
            'dims.emotions': 'Cảm xúc',
            'dims.negative': 'Tiêu cực',
            'dims.positive': 'Tích cực',
            'dims.creativity': 'Sáng tạo',
            'dims.overview': 'Tổng quan',


            /* ══ TASKS PAGE ══════════════════════════════ */
            'tasks.title': 'Nhiệm Vụ',
            'tasks.work_history': 'Lịch Sử Làm Việc',
            'tasks.all_sessions': 'Tất Cả Phiên Làm Việc',
            'tasks.plan': 'Nhiệm Vụ',
            'tasks.do': 'Đang Thực Hiện',
            'tasks.check': 'Hoàn Thành',
            'tasks.act': 'Cải Tiến',
            'tasks.no_goal': 'Chưa Thiết Lập Mục Tiêu...',
            'tasks.complete': 'Hoàn Thành',
            'tasks.ai_review': 'Đã Được AI Review',
            'tasks.new_task_btn': '+ Nhiệm Vụ Mới',

            /* ══ ANALYTICS PAGE ══════════════════════════ */
            'analytics.title': 'Đánh giá của người dùng',
            'analytics.description': 'Đo lường chất lượng quyết định và mức độ duy trì tư duy hệ thống sau quá trình huấn luyện và rèn luyện cùng Thapsang Framework.',
            'analytics.survey': 'Khảo Sát Đánh Giá Hiệu Quả Nhận Thức',
            'analytics.survey_desc': 'Đánh giá mức độ đồng ý của bạn với các tiêu chí (1: Không đồng ý, 5: Cực kỳ đồng ý)',
            'analytics.criteria': 'TIÊU CHÍ ĐÁNH GIÁ & PHẢN CHIẾU',
            'analytics.not_sat': 'Không hài lòng',
            'analytics.very_sat': 'Rất hài lòng',
            'analytics.reset': 'Đặt lại',
            'analytics.group1': 'NHÓM 1: CHẤT LƯỢNG QUYẾT ĐỊNH',
            'analytics.group2': 'NHÓM 2: DUY TRÌ TƯ DUY HỆ THỐNG',
            'analytics.group3': 'NHÓM 3: HÀNH ĐỘNG & THAY ĐỔI HÀNH VI',
            'analytics.confirm_reset_title': 'Xác nhận đặt lại?',
            'analytics.confirm_reset_desc': 'Tất cả các câu trả lời khảo sát và phân tích AI sẽ được đưa về giá trị mặc định ban đầu.',
            'analytics.cancel': 'Hủy',
            'analytics.confirm': 'Đồng ý',
            'analytics.q1_title': '1. Xác định Mục tiêu & Giải pháp',
            'analytics.q1_desc': 'Thapsang Framework giúp tôi xác định rõ ràng mục tiêu cốt lõi và các giải pháp khả thi khi đưa ra quyết định lớn.',
            'analytics.q2_title': '2. Phản chiếu Socratic & Nhận diện Thiên kiến',
            'analytics.q2_desc': 'Quá trình trò chuyện với AI Coach và sơ đồ niềm tin giúp tôi phát hiện mâu thuẫn nhận thức và ngụy biện logic để quyết định khách quan hơn.',
            'analytics.q3_title': '3. Mức độ Hài lòng với Kết quả Quyết định',
            'analytics.q3_desc': 'Tôi hoàn toàn cảm thấy hài lòng và tin tưởng vào các quyết định lớn của mình sau khi chúng được kiểm chứng thông qua Framework.',
            'analytics.q4_title': '4. Thói quen thiết lập Bản đồ Tư duy (Mindmap Creation)',
            'analytics.q4_desc': 'Tôi vẫn duy trì thói quen vẽ mindmap hoặc sơ đồ liên kết tư duy để phân tích cấu trúc tổng quan của các vấn đề phức tạp sau 6 tháng.',
            'analytics.q5_title': '5. Vận dụng PDCA (Plan-Do-Check-Act) thường nhật',
            'analytics.q5_desc': 'Thói quen lập kế hoạch hành động và xem xét phản hồi (Reflection) theo chu trình PDCA được lồng ghép tự nhiên vào công việc và cuộc sống của tôi.',
            'analytics.q6_title': '6. Tự phản chiếu Nhận thức (Cognitive Self-Reflection)',
            'analytics.q6_desc': 'Sau 6 tháng, tôi có khả năng tự đặt câu hỏi Socratic sắc bén để tự chẩn đoán phản chiếu tư duy khi gặp bế tắc.',
            'analytics.submit_desc': 'Dữ liệu đánh giá cá nhân sẽ lập tức được AI phân tích và ánh xạ vào biểu đồ xu hướng.',
            'analytics.submit_btn': 'Gửi đánh giá',
            'analytics.fw_metric': 'Chỉ số Framework',
            'analytics.metric_dq': 'Chất lượng Quyết định',
            'analytics.metric_dq_badge': 'Chất lượng quyết định',
            'analytics.ai_insight_label': 'Phân tích AI:',
            'analytics.ai_insight_desc': 'Tỷ lệ người dùng cảm thấy hài lòng với các quyết định lớn sau khi đi qua hệ thống Thapsang. Chỉ số được tính toán dựa trên mức độ hài lòng thực tế và khả năng phát hiện ngụy biến tư duy.',
            'analytics.ai_reanalyzing': 'AI đang tái phân tích...',
            'analytics.metric_retention_period': 'Duy trì sau 6 tháng',
            'analytics.metric_retention': 'Duy trì tư duy hệ thống',
            'analytics.metric_retention_badge': 'Duy trì tư duy hệ thống',
            'analytics.ai_predictive_label': 'Mô hình Dự đoán AI:',
            'analytics.ai_predictive_desc': 'Đo lường khả năng duy trì các thói quen tư duy hệ thống (vẽ mindmap, chu trình PDCA, tự chẩn đoán phản chiếu) sau 6 tháng kể từ khi gia nhập Thapsang OS.',
            'analytics.submitting_msg': 'Hệ thống đang gửi đánh giá và đồng bộ',
            'analytics.submit_success': 'Gửi thành công!',
            'analytics.conn_error': 'Không thể kết nối đến máy chủ. Vui lòng thử lại sau!',

            /* ══ COHORT PAGE ═════════════════════════════ */
            'cohort.active': 'HOẠT ĐỘNG',
            'cohort.week': 'Tuần',
            'cohort.study_path': 'Lộ trình học tập',
            'cohort.map_ai': 'Map mục tiêu với AI',
            'cohort.your_progress': 'Tiến độ của bạn',
            'cohort.this_week': 'Tuần này',
            'cohort.individual': 'Cá nhân',
            'cohort.group_avg': 'Trung bình nhóm',
            'cohort.week_desc': 'bản đồ tư duy tuần 1 — nút đỏ là điểm nghẽn cần Unlearn.',
            'cohort.full_aoa': 'Xem full trên AOA Feed',
            'cohort.loading': 'Đang tải lịch trình...',
            'cohort.completed': 'Hoàn thành',
            'cohort.present': 'Hiện tại',
            'cohort.upcoming': 'Sắp tới',
            'cohort.core': 'Cốt lõi',
            'cohort.supp': 'Phụ trợ',
            'cohort.added': 'Đã thêm',
            'cohort.add_task': '+ Thêm vào Task',
            'cohort.added_msg': 'task đã thêm vào danh sách cá nhân',
            'cohort.view_do': 'Xem tiến độ DO',
            'cohort.heatmap_title': 'Biểu đồ tiến độ nhóm',
            'cohort.group_avg_progress': 'Tiến độ trung bình nhóm',
            'cohort.personal_tasks_title': 'Nhiệm vụ cá nhân của bạn',
            'cohort.live_resonance': 'Cộng hưởng trực tiếp',
            'cohort.dynamic_pivot': 'Điều chỉnh linh hoạt',
            'cohort.auto_triggered': 'Tự động kích hoạt',

            /* ── Cohort Dynamic Syllabus ── */
            "The Great Rebuild": "Tái Thiết Vĩ Đại",
            "Unlearn: Phá vỡ định kiến": "Học cách quên: Phá vỡ định kiến",
            "Nhận diện và tháo gỡ các rào cản tâm lý cũ đang kìm hãm bạn.": "Nhận diện và tháo gỡ các rào cản tâm lý cũ đang kìm hãm bạn.",
            "Viết nhật ký 'Tôi không thể...' trong 7 ngày": "Viết nhật ký 'Tôi không thể...' trong 7 ngày",
            "Thực hành phiên Soi chiếu Socratic với AI Coach": "Thực hành phiên Soi chiếu Socratic với AI Coach",
            "Mapping Baseline Mind Map (Bản đồ tư duy hiện tại)": "Mapping Baseline Mind Map (Bản đồ tư duy hiện tại)",
            "Đọc: Chương 1 - Mindset (Carol Dweck)": "Đọc: Chương 1 - Mindset (Carol Dweck)",
            "Relearn: Thiết lập hệ thống Habit": "Học lại: Thiết lập hệ thống Habit",
            "Xây dựng framework tư duy mới và thử nghiệm các khuôn mẫu hành vi tích cực.": "Xây dựng framework tư duy mới và thử nghiệm các khuôn mẫu hành vi tích cực.",
            "Xây dựng Routine buổi sáng (Morning Protocol)": "Xây dựng Routine buổi sáng (Morning Protocol)",
            "Định nghĩa lại khái niệm 'Nghỉ ngơi' cho bản thân": "Định nghĩa lại khái niệm 'Nghỉ ngơi' cho bản thân",
            "Cài đặt 1 Implementation Intention mới": "Cài đặt 1 Implementation Intention mới",
            "Nghe Podcast: Quản trị Năng lượng - Andrew Huberman": "Nghe Podcast: Quản trị Năng lượng - Andrew Huberman",
            "Relearn: Deep Work & Quản lý Sự chú ý": "Học lại: Deep Work & Quản lý Sự chú ý",
            "Học cách bảo vệ sự tập trung và thiết kế môi trường làm việc tối ưu.": "Học cách bảo vệ sự tập trung và thiết kế môi trường làm việc tối ưu.",
            "Thiết kế 2 khung giờ Deep Work mỗi ngày": "Thiết kế 2 khung giờ Deep Work mỗi ngày",
            "Audit và loại bỏ 3 tác nhân phân tâm lớn nhất": "Audit và loại bỏ 3 tác nhân phân tâm lớn nhất",
            "Thực hành Time Blocking trong 5 ngày": "Thực hành Time Blocking trong 5 ngày",
            "Đọc: Deep Work - Cal Newport (Phần 1)": "Đọc: Deep Work - Cal Newport (Phần 1)",
        },

        en: {
            /* ── Sidebar navigation ── */
            'nav.coach': 'Coach',
            'nav.diary': 'Diary',
            'nav.aoa': 'AOA Feed',
            'nav.tasks': 'Tasks',
            'nav.analytics': 'Analytics',
            'nav.cohort': 'Personal Roadmap',
            'nav.personal_roadmap': 'Personal Roadmap',

            /* ── Sidebar footer ── */
            'sidebar.tagline': 'Mindset OS',
            'sidebar.logout': 'Log Out',
            'common.switch_theme': 'Switch Theme',

            /* ── Settings panel ── */
            'settings.title': 'Settings',
            'settings.language': 'Language',

            /* ══ LOGIN PAGE ══════════════════════════════ */
            'login.tab_login': 'Login',
            'login.tab_register': 'Register',
            'login.email': 'Email',
            'login.email_ph': 'Enter email...',
            'login.email_example': 'example@email.com',
            'login.password': 'Password',
            'login.remember': 'Remember me',
            'login.forgot_pwd': 'Forgot password?',
            'login.btn_login': 'Log in',
            'login.fullname': 'Full name',
            'login.fullname_ph': 'Enter your full name...',
            'login.confirm_password': 'Confirm password',
            'login.btn_register': 'Create account',
            'login.otp_title': 'Confirm OTP',
            'login.otp_desc': 'Please enter the 6-character code sent to your email',
            'login.otp_label': 'OTP Code',
            'login.btn_otp': 'Confirm & Login',
            'login.forgot_title': 'Reset Password',
            'login.forgot_desc': 'Enter your registered email to receive a recovery code.',
            'login.btn_send_otp': 'Send recovery code',
            'login.confirm_otp_title': 'Confirm Code',
            'login.confirm_otp_desc': 'Please enter the 6-character code sent to',
            'login.btn_continue': 'Continue',
            'login.new_pwd_title': 'Create New Password',
            'login.new_pwd_label': 'New password',
            'login.btn_reset_pwd': 'Reset password',
            'login.msg_recovery_sent': 'Recovery code sent to your email!',
            'login.msg_sys_error': 'System error',
            'login.msg_conn_error': 'Unable to connect to server',
            'login.msg_otp_valid': 'Valid code, please create a new password.',
            'login.msg_pwd_mismatch': 'Passwords do not match!',
            'login.msg_pwd_changed': 'Password changed successfully! Please log in.',
            'login.msg_otp_sent': 'OTP code sent! Please check your email.',
            'login.msg_required': 'Please fill out this field.',
            'login.msg_email_invalid': 'Please enter a valid email address.',
            /* Backend Errors */
            'Sai thông tin đăng nhập': 'Invalid credentials',
            'Tài khoản đã tồn tại': 'Account already exists',
            'Mã OTP không hợp lệ hoặc đã hết hạn': 'Invalid or expired OTP code',
            'Email không tồn tại trong hệ thống': 'Email does not exist in the system',
            'Không tìm thấy tài khoản': 'Account not found',
            'Số lần nhập sai đã hơn 5 lần, vui lòng thử lại sau.': 'More than 5 failed attempts, please try again later.',
            'Mật khẩu mới phải khác với 3 mật khẩu gần đây nhất.': 'New password must be different from the last 3 passwords.',
            'Mật khẩu phải bao gồm cả chữ và số.': 'Password must contain both letters and numbers.',
            'Mật khẩu không hợp lệ theo quy tắc của hệ thống.': 'Invalid password according to system rules.',

            /* ══ ONBOARDING PAGE ════════════════════════════ */
            'ob.welcome': 'Welcome',
            'ob.tagline': 'Mindset OS',
            'ob.q_dob': 'What is your date of birth?',
            'ob.sub_dob': 'Help us personalize your experience',
            'ob.day': 'Day',
            'ob.month': 'Month',
            'ob.year': 'Year',
            'ob.q_gender': 'What is your gender?',
            'ob.sub_gender': 'This information is completely confidential',
            'ob.q_interests': 'What are your interests?',
            'ob.sub_interests': 'Select all that apply to you',
            'ob.q_problems': 'What problems are you facing?',
            'ob.sub_problems': 'Coach AI will help you solve these problems',
            'ob.q_goals': 'Your goals for using the app?',
            'ob.sub_goals': 'We will optimize the experience according to your goals',
            'ob.q_source': 'How did you hear about Thapsang?',
            'ob.sub_source': 'Help us improve our outreach experience',
            'ob.btn_back': 'Back',
            'ob.btn_next': 'Next',
            'ob.btn_start': 'Start your journey',
            'ob.btn_saving': 'Saving...',
            'ob.btn_skip': 'Skip, I will explore later →',

            /* Onboarding Options */
            'Nam': 'Male', 'Nữ': 'Female', 'Khác': 'Other', 'Không muốn tiết lộ': 'Prefer not to say',
            'Đọc sách': 'Reading', 'Thể thao': 'Sports', 'Âm nhạc': 'Music', 'Du lịch': 'Travel', 'Công nghệ': 'Technology', 'Nghệ thuật': 'Art', 'Nấu ăn': 'Cooking', 'Thiền & Yoga': 'Meditation & Yoga', 'Viết lách': 'Writing', 'Phim ảnh': 'Movies',
            'Căng thẳng / Stress': 'Stress', 'Mất tập trung': 'Lack of focus', 'Thiếu động lực': 'Lack of motivation', 'Mất ngủ': 'Insomnia', 'Lo âu': 'Anxiety', 'Khó kiểm soát cảm xúc': 'Emotional instability', 'Thiếu mục tiêu sống': 'Lack of life goals', 'Cô đơn': 'Loneliness', 'Trì hoãn': 'Procrastination', 'Tự ti': 'Low self-esteem',
            'Quản lý cảm xúc': 'Emotional management', 'Phát triển bản thân': 'Self-development', 'Tăng năng suất': 'Increase productivity', 'Cải thiện giấc ngủ': 'Improve sleep', 'Xây dựng thói quen tốt': 'Build good habits', 'Tìm hiểu bản thân': 'Self-discovery', 'Kết nối cộng đồng': 'Community connection', 'Giảm căng thẳng': 'Reduce stress',
            'Bạn bè giới thiệu': 'Friend referral', 'Mạng xã hội': 'Social media', 'Tìm kiếm Google': 'Google search', 'Báo chí / Truyền thông': 'Press / Media', 'Trường học / Công ty': 'School / Company',

            /* ══ COACH PAGE ══════════════════════════════ */
            'coach.title': 'Socratic Dialogue',
            'coach.subtitle': 'Filtering the noise. Finding the core.',
            'coach.welcome_prefix': 'Welcome ',
            'coach.welcome_suffix': '. What is on your mind?',
            'coach.history': 'History',
            'coach.sessions': 'Chat sessions',
            'coach.no_history': 'No history yet',
            'coach.post': 'Post',
            'coach.topography': 'Mind Map',
            'coach.no_mindmap_data': '',
            'coach.new_task': 'New\nTask',
            'coach.tasks': 'Task',
            'coach.placeholder': 'Type your thoughts...',
            'coach.thinking': 'Inner thought stream...',
            'coach.center_map': 'Center map',
            'coach.regenerate': 'Regenerate',
            'coach.play_voice': 'Play voice',
            'coach.diary_consent_prompt': 'We have gathered enough data to reflect on what you shared. Would you like the AI Coach to generate and update a note in your Diary?',
            'coach.diary_consent_always': 'Always agree to auto-generate diary (skip this prompt in the future)',
            'coach.diary_consent_decline': 'Decline',
            'coach.diary_consent_accept': 'Accept',
            'coach.diary_consent_toast': 'Requested AI to generate diary in the background...',

            /* ══ DIARY PAGE ══════════════════════════════ */
            'diary.vault': 'Thapsang Core',
            'diary.draft': 'Draft',
            'diary.preview': 'Preview',
            'diary.root_files': 'ROOT FILES',
            'diary.search': 'Search documents...',
            'diary.mirror': 'Reflective Mirror',
            'diary.synced': 'Synced',
            'diary.syncing': 'Syncing...',
            'diary.new_note': 'Create new note',
            'diary.graph_desc': 'Visual map of connections between your notes and folders. Click a node to open that note quickly.',
            'diary.words': 'words',
            'diary.chars': 'chars',
            'diary.today': 'Today',
            'diary.ai_reflecting': 'AI reflecting...',
            'diary.save': 'Save',
            'diary.title_ph': 'Diary title...',
            'diary.content_ph': 'Start typing your deep reflections here...',
            'diary.new_folder': 'Create new folder',
            'diary.sort': 'Sort list',
            'diary.sort_newest': 'Newest',
            'diary.sort_oldest': 'Oldest',
            'diary.sort_alpha': 'Name A - Z',
            'diary.delete_folder': 'Delete this folder',
            'diary.focus_mode': 'Focus Mode',
            'diary.exit_focus_mode': 'Exit Focus Mode',
            'diary.close_panel': 'Close panel',
            'diary.building_graph': 'Building graph view...',
            'diary.untitled': 'Untitled',
            'diary.modal_label': 'Name / Title',
            'diary.cancel': 'Cancel',
            'diary.create_btn': 'Create',
            'diary.confirm_delete': 'Confirm Delete',
            'diary.create_note_title': 'Create new note',
            'diary.create_note_ph': 'Enter note title...',
            'diary.create_folder_title': 'Create new folder',
            'diary.create_folder_ph': 'Enter folder name...',
            'diary.delete_note_title': 'Confirm Delete Note',
            'diary.delete_note_msg': 'Are you sure you want to permanently delete the note "{title}"? This action cannot be undone.',
            'diary.delete_folder_title': 'Confirm Delete Folder',
            'diary.delete_folder_msg_with_notes': 'The folder "{folder}" contains {count} notes. Deleting this folder will PERMANENTLY delete the entire folder and all notes inside. Are you sure you want to continue?',
            'diary.delete_folder_msg_empty': 'Are you sure you want to delete the empty folder "{folder}"?',
            'diary.toast_load_err': 'Unable to load diary entries from server.',
            'diary.toast_sort_info': 'Document list sorted.',
            'diary.toast_create_note_ok': 'New note created successfully!',
            'diary.toast_create_note_fail': 'Failed to save new note.',
            'diary.toast_folder_exists': 'Folder already exists.',
            'diary.toast_create_folder_ok': 'Folder "{folder}" created successfully!',
            'diary.toast_create_folder_fail': 'Failed to create new folder.',
            'diary.toast_ai_reflecting': 'AI Coach is reflecting on life with you...',
            'diary.toast_save_ok': 'Note accepted by AI',
            'diary.toast_save_fail': 'Failed to save note.',
            'diary.toast_deleting_note': 'Deleting note...',
            'diary.toast_delete_draft_ok': 'Draft note deleted.',
            'diary.toast_delete_note_ok': 'Note deleted successfully.',
            'diary.toast_delete_note_fail': 'Failed to delete note.',
            'diary.toast_deleting_folder': 'Deleting folder...',
            'diary.toast_delete_folder_ok': 'Folder "{folder}" deleted successfully!',
            'diary.toast_delete_folder_fail': 'Could not fully delete folder.',
            'diary.toast_auto_creating': 'Automatically creating note "{title}"...',
            'diary.toast_auto_create_ok': 'Linked & created note "{title}" successfully!',
            'diary.toast_auto_create_fail': 'Failed to automatically create note.',
            'diary.import_files': 'Import Files',
            'diary.import_folder': 'Import Folder',
            'diary.export': 'Export Document',

            /* ══ AOA FEED PAGE ═══════════════════════════ */
            'aoa.title': 'Ask Others Anything',
            'aoa.community': 'Community',
            'aoa.trending': 'Trending',
            'aoa.profile': 'My Profile',
            'aoa.search': 'Search posts...',
            'aoa.new_post': 'New Post',
            'aoa.share_mind': 'Share your thoughts...',
            'aoa.publish': 'Publish',
            'aoa.following': 'Following',
            'aoa.follow': 'Follow',
            'aoa.no_posts': 'No posts yet.',
            'aoa.content_mgmt': 'Content Management',
            'aoa.hidden_posts': 'Hidden Posts',
            'aoa.hidden_posts_desc': 'Posts you do not want to see',
            'aoa.deleted_posts': 'Deleted Posts',
            'aoa.deleted_posts_desc': 'Your trash / recycle bin',
            'aoa.hidden_title': 'Hidden Posts',
            'aoa.deleted_title': 'Deleted Posts',
            'aoa.hidden_title_desc': 'List of posts archived separately',
            'aoa.deleted_title_desc': 'Posts will be deleted automatically after 30 days',
            'aoa.back': 'Back',
            'aoa.no_more_posts': 'You have seen all posts',
            'aoa.privacy_public': 'Public',
            'aoa.privacy_followers': 'Followers only',
            'aoa.privacy_private': 'Private',

            /* -- AOA Added translation keys -- */
            'aoa.ai_report_title': 'Trending Topics',
            'aoa.compiling_community': 'Compiling community data...',
            'aoa.analysis_posts': 'Analysis Posts',
            'aoa.interactions': 'Interactions',
            'aoa.trending_posts': 'Trending Content',
            'aoa.loading_pathway': 'Loading pathway...',
            'aoa.coach_suggestions': 'Recommended Coaches',
            'aoa.sort_by': 'Sort by:',
            'aoa.influence': 'Influence',
            'aoa.followers': 'Followers',
            'aoa.name_az': 'Name (A-Z)',
            'aoa.followers_count': 'followers',
            'aoa.ask_ai_coach': 'Ask AI Coach',
            'aoa.send_message': 'Message',
            'aoa.view_mindmap': 'View Mindmap',
            'aoa.explore_experts_link': 'Explore more experts',
            'aoa.explore_experts_title': 'Explore Thapsang Experts',
            'aoa.explore_experts_desc': 'Find and follow the best AI Mentors & Cognitive Support Experts.',
            'aoa.explore_search_ph': 'Search experts by name, bio or keyword...',
            'aoa.tag_all': 'All',
            'aoa.tag_ai_mentor': 'AI Mentor',
            'aoa.tag_expert': 'Expert',
            'aoa.tag_mindset': 'Mindset',
            'aoa.tag_psychology': 'Psychology',
            'aoa.ai_analyzing_mindset': 'AI is analyzing mindset...',
            'aoa.mindmap_title': 'Mindmap',
            'aoa.ai_live_scan': 'AI Live Scan',
            'aoa.behavioral_analysis': 'Behavioral Analysis',
            'aoa.not_enough_data_keywords': 'Not enough data to analyze',
            'aoa.ai_analyzing_data': 'AI is analyzing your data...',
            'aoa.mbti_classification': 'MBTI Personality Classification',
            'aoa.mbti_not_enough_data': 'AI does not have enough data for MBTI classification. Please share more!',
            'aoa.dim_objective': 'Objective',
            'aoa.dim_emotion': 'Emotion',
            'aoa.dim_negative': 'Negative',
            'aoa.dim_positive': 'Positive',
            'aoa.dim_creativity': 'Creativity',
            'aoa.dim_overview': 'Overview',
            'aoa.tag_strategy': 'Strategy',
            'aoa.core_expertise': 'Core expertise: ',
            'aoa.no_experts_found': 'No matching experts found',
            'aoa.edit_profile': 'Edit Profile',
            'aoa.profile_settings': 'Profile Settings',
            'aoa.cancel': 'Cancel',
            'aoa.save_changes': 'Save Changes',
            'aoa.display_name': 'Display Name',
            'aoa.display_name_tip': 'Tip: Display name helps people identify you more easily.',
            'aoa.account_id_static': 'Account ID (Static)',
            'aoa.account_id_tip': 'This ID is fixed to preserve your post history.',
            'aoa.bio_label': 'Introduce yourself',
            'aoa.default_bio': 'Learning, sharing and growing together at Thapsang community. Passionate about knowledge and creativity.',
            'aoa.my_posts': 'My Posts',
            'aoa.posts': 'Posts',
            'aoa.mindset_metrics': 'Mindset indicators',
            'aoa.mind_map': 'Mind Map',
            'aoa.ai_live_scan': 'AI Live Scan',
            'aoa.zoom_mindmap': 'Zoom mind map',
            'aoa.behavioral_analysis': 'Behavioral Analysis',
            'aoa.insufficient_data': 'Not enough data for analysis',
            'aoa.mbti_classification': 'MBTI Personality Classification',
            'aoa.mbti_insufficient_data': 'AI has not enough data to classify MBTI. Please share more!',
            'aoa.close': 'Close',
            'aoa.ai_mindset_map': 'AI Mindset Map',
            'aoa.tactical_display': 'Detailed Analysis Mode',
            'aoa.interactive_map_desc': 'Accurate interactive mind map based on real-time data.',
            'aoa.zoom_mindmap': 'Zoom Mind Map',
            'aoa.detailed_analysis_mode': 'Detailed Analysis Mode',
            'aoa.interactive_mindmap_realtime': 'Interactive mind map accurately based on real-time data.',
            'aoa.ai_analyzing_mindset': 'AI is analyzing mindset...',
            'aoa.add_comment_ph': 'Add your comment...',
            'aoa.comment_ph': 'Comment...',
            'aoa.share_post_title': 'Share Post',
            'aoa.repost_comment_ph': 'Add your comment...',
            'aoa.sharing_thoughts': 'Sharing thoughts...',
            'aoa.shared_success_title': 'Shared!',
            'aoa.shared_success_desc': 'The post was successfully reposted to My Posts.',
            'aoa.awesome': 'Awesome',
            'aoa.hide_post': 'Hide post',
            'aoa.unhide_post': 'Unhide post',
            'aoa.unhide_post_msg': 'The post will return to the community feed.',
            'aoa.hide_post_msg': 'You will not see this post on the feed anymore.',
            'aoa.save_post': 'Save post',
            'aoa.unsave_post': 'Unsave post',
            'aoa.report_post': 'Report',
            'aoa.restore_post': 'Restore post',
            'aoa.edit_post': 'Edit post',
            'aoa.delete_post': 'Delete post',
            'aoa.thank_you': 'Thank you',
            'aoa.report_received': 'We have recorded your report.',
            'aoa.delete_permanent': 'Permanently delete',
            'aoa.delete_confirm': 'Confirm delete',
            'aoa.delete_permanent_msg': 'This action will permanently delete the post from the system.',
            'aoa.delete_confirm_msg': 'The post will be moved to \'Deleted Posts\'.',
            'aoa.restored_title': 'Restored',
            'aoa.restored_msg': 'The post has been brought back to the main feed.',
            'aoa.success_sync': 'Your profile has been updated successfully!',
            'aoa.error_sync': 'Unable to sync to the server. Please check your connection and try again.',
            'aoa.post_by': 'Post by',
            'aoa.original_post': 'Original post:',
            'aoa.reposted': 'reposted',
            'aoa.likes_label': 'Likes',
            'aoa.followers_label': 'Followers',
            'aoa.following_label': 'Following',
            'aoa.mbti_tip': 'Based on work habits and interaction',
            'aoa.trending_label': 'Trending',
            'aoa.viral_content': 'Viral Content',
            'aoa.based_on_community': 'Based on community content analysis',
            'aoa.engagement_score': 'engagement points',
            'aoa.loading_more': 'Loading more...',

            'dims.objective': 'Objective',
            'dims.emotions': 'Emotions',
            'dims.negative': 'Negative',
            'dims.positive': 'Positive',
            'dims.creativity': 'Creativity',
            'dims.overview': 'Overview',


            /* ══ TASKS PAGE ══════════════════════════════ */
            'tasks.title': 'Tasks',
            'tasks.work_history': 'Work History',
            'tasks.all_sessions': 'All sessions',
            'tasks.plan': 'Tasks',
            'tasks.do': 'In Progress',
            'tasks.check': 'Done',
            'tasks.act': 'Act',
            'tasks.no_goal': 'No goal set yet...',
            'tasks.complete': 'Complete',
            'tasks.ai_review': 'AI Reviewed',
            'tasks.new_task_btn': '+ New Task',

            /* ══ ANALYTICS PAGE ══════════════════════════ */
            'analytics.title': 'User Assessment',
            'analytics.description': 'Measure decision quality and systems-thinking retention after training with the Thapsang Framework.',
            'analytics.survey': 'Cognitive Effectiveness Survey',
            'analytics.survey_desc': 'Rate your agreement with each criterion (1 = Strongly Disagree, 5 = Strongly Agree)',
            'analytics.criteria': 'ASSESSMENT CRITERIA & REFLECTION',
            'analytics.not_sat': 'Not satisfied',
            'analytics.very_sat': 'Very satisfied',
            'analytics.reset': 'Reset',
            'analytics.group1': 'GROUP 1: DECISION QUALITY',
            'analytics.group2': 'GROUP 2: RETENTION OF MINDSET (6 MONTHS LATER)',
            'analytics.group3': 'GROUP 3: ACTION & BEHAVIOR CHANGE',
            'analytics.confirm_reset_title': 'Confirm reset?',
            'analytics.confirm_reset_desc': 'All survey answers and AI analytics will be reverted to initial defaults.',
            'analytics.cancel': 'Cancel',
            'analytics.confirm': 'Confirm',
            'analytics.q1_title': '1. Define Goals & Solutions',
            'analytics.q1_desc': 'Thapsang Framework helps me clarify core goals and viable options when making major decisions.',
            'analytics.q2_title': '2. Socratic Reflection & Bias Detection',
            'analytics.q2_desc': 'Interactions with AI Coach and the belief map help me identify cognitive dissonance and logical fallacies to decide more objectively.',
            'analytics.q3_title': '3. Satisfaction with Decision Outcomes',
            'analytics.q3_desc': 'I feel fully satisfied and confident in my major decisions after they are validated through the Framework.',
            'analytics.q4_title': '4. Mindmap Creation Habit',
            'analytics.q4_desc': 'I maintain the habit of drawing mindmaps or cognitive connection diagrams to analyze complex structural outlines after 6 months.',
            'analytics.q5_title': '5. Daily PDCA (Plan-Do-Check-Act) Application',
            'analytics.q5_desc': 'The habit of action planning and reflection within the PDCA cycle is naturally integrated into my work and daily life.',
            'analytics.q6_title': '6. Cognitive Self-Reflection',
            'analytics.q6_desc': 'After 6 months, I am capable of asking sharp Socratic questions to self-diagnose cognitive bottlenecks when stuck.',
            'analytics.submit_desc': 'Personal assessment data will instantly be analyzed by AI and mapped to the trend charts.',
            'analytics.submit_btn': 'Submit Assessment',
            'analytics.fw_metric': 'Framework Metric',
            'analytics.metric_dq': 'Decision Quality',
            'analytics.metric_dq_badge': 'Decision Quality',
            'analytics.ai_insight_label': 'AI Insight:',
            'analytics.ai_insight_desc': 'The percentage of users who feel satisfied with major decisions after using the Thapsang system. The metric is calculated based on real satisfaction level and cognitive bias detection capability.',
            'analytics.ai_reanalyzing': 'AI is re-analyzing...',
            'analytics.metric_retention_period': '6-Month Retention',
            'analytics.metric_retention': 'Retention of Mindset',
            'analytics.metric_retention_badge': 'Retention of Mindset',
            'analytics.ai_predictive_label': 'AI Predictive Modeling:',
            'analytics.ai_predictive_desc': 'Measures the retention of system-thinking habits (mindmapping, PDCA cycle, cognitive self-reflection) 6 months after joining Thapsang OS.',
            'analytics.submitting_msg': 'System is submitting assessments and synchronizing...',
            'analytics.submit_success': 'Success!',
            'analytics.conn_error': 'Unable to connect to the server. Please try again later!',

            /* ══ COHORT PAGE ═════════════════════════════ */
            'cohort.active': 'ACTIVE',
            'cohort.week': 'Week',
            'cohort.study_path': 'Study Pathway',
            'cohort.map_ai': 'Map goals with AI',
            'cohort.your_progress': 'Your progress',
            'cohort.this_week': 'This week',
            'cohort.individual': 'Individual',
            'cohort.group_avg': 'Group average',
            'cohort.week_desc': 'Baseline Mind Map week 1 — red dot is the bottleneck to Unlearn.',
            'cohort.full_aoa': 'View full on AOA Feed',
            'cohort.loading': 'Loading pathway...',
            'cohort.completed': 'Completed',
            'cohort.present': 'Present',
            'cohort.upcoming': 'Upcoming',
            'cohort.core': 'Core',
            'cohort.supp': 'Supplementary',
            'cohort.added': 'Added',
            'cohort.add_task': '+ Add to Tasks',
            'cohort.added_msg': 'tasks added to individual list',
            'cohort.view_do': 'View DO progress',
            'cohort.heatmap_title': 'Cohort Progress Heatmap',
            'cohort.group_avg_progress': 'Group average progress',
            'cohort.personal_tasks_title': 'Your Cohort Tasks',
            'cohort.live_resonance': 'Live Resonance',
            'cohort.dynamic_pivot': 'Dynamic Pivot',
            'cohort.auto_triggered': 'Auto-triggered',

            /* ── Cohort Dynamic Syllabus ── */
            "The Great Rebuild": "The Great Rebuild",
            "Unlearn: Phá vỡ định kiến": "Unlearn: Breaking Biases",
            "Nhận diện và tháo gỡ các rào cản tâm lý cũ đang kìm hãm bạn.": "Identify and dismantle the old psychological barriers holding you back.",
            "Viết nhật ký 'Tôi không thể...' trong 7 ngày": "Journal 'I cannot...' for 7 days",
            "Thực hành phiên Soi chiếu Socratic với AI Coach": "Practice a Socratic Reflection session with AI Coach",
            "Mapping Baseline Mind Map (Bản đồ tư duy hiện tại)": "Map your Baseline Mind Map (Current mind map)",
            "Đọc: Chương 1 - Mindset (Carol Dweck)": "Read: Chapter 1 - Mindset (Carol Dweck)",
            "Relearn: Thiết lập hệ thống Habit": "Relearn: Building Habit Systems",
            "Xây dựng framework tư duy mới và thử nghiệm các khuôn mẫu hành vi tích cực.": "Build new mental frameworks and test positive behavioral patterns.",
            "Xây dựng Routine buổi sáng (Morning Protocol)": "Build a Morning Routine (Morning Protocol)",
            "Định nghĩa lại khái niệm 'Nghỉ ngơi' cho bản thân": "Redefine the concept of 'Rest' for yourself",
            "Cài đặt 1 Implementation Intention mới": "Set 1 new Implementation Intention",
            "Nghe Podcast: Quản trị Năng lượng - Andrew Huberman": "Listen to Podcast: Energy Management - Andrew Huberman",
            "Relearn: Deep Work & Quản lý Sự chú ý": "Relearn: Deep Work & Attention Management",
            "Học cách bảo vệ sự tập trung và thiết kế môi trường làm việc tối ưu.": "Learn how to protect focus and design an optimal work environment.",
            "Thiết kế 2 khung giờ Deep Work mỗi ngày": "Design 2 Deep Work time blocks daily",
            "Audit và loại bỏ 3 tác nhân phân tâm lớn nhất": "Audit and eliminate the 3 biggest distractions",
            "Thực hành Time Blocking trong 5 ngày": "Practice Time Blocking for 5 days",
            "Đọc: Deep Work - Cal Newport (Phần 1)": "Read: Deep Work - Cal Newport (Part 1)",
        }
    };

    /* ══════════════════════════════════════════════════════
       PUBLIC API
    ══════════════════════════════════════════════════════ */
    window.t = function (key) {
        const dict = translations[window.currentLang] || translations['vi'];
        return dict[key] !== undefined ? dict[key] : key;
    };

    window.setLang = function (lang) {
        if (lang === window.currentLang) return;
        localStorage.setItem(LANG_KEY, lang);
        window.currentLang = lang;
        _applyAll();
        window.dispatchEvent(new CustomEvent('ts-lang-changed', { detail: { lang: window.currentLang } }));
    };

    window.toggleLang = function () {
        const nextLang = window.currentLang === 'vi' ? 'en' : 'vi';
        window.setLang(nextLang);
    };

    window.toggleSettingsPanel = function () {
        const panel = document.getElementById('ts-settings-panel');
        const icon = document.getElementById('ts-settings-icon');
        if (!panel) return;
        const opening = panel.classList.contains('ts-panel-hidden');
        panel.classList.toggle('ts-panel-hidden');
        if (icon) icon.style.transform = opening ? 'rotate(90deg)' : 'rotate(0deg)';
    };

    window.toggleTheme = function () {
        const nextTheme = window.currentTheme === 'dark' ? 'light' : 'dark';
        window.setTheme(nextTheme);
    };

    window.setTheme = function (theme) {
        localStorage.setItem(THEME_KEY, theme);
        localStorage.setItem('theme', theme);
        window.currentTheme = theme;
        _applyTheme();
    };

    function _applyTheme() {
        const isDark = window.currentTheme === 'dark';
        document.documentElement.classList.toggle('dark', isDark);
        document.documentElement.classList.toggle('light', !isDark);

        document.querySelectorAll('#ts-theme-icon').forEach(function (el) {
            el.textContent = isDark ? 'light_mode' : 'dark_mode';
        });

        window.dispatchEvent(new CustomEvent('ts-theme-changed', { detail: { theme: window.currentTheme } }));
    }

    /* ══════════════════════════════════════════════════════
       INTERNAL HELPERS
    ══════════════════════════════════════════════════════ */
    let isTranslating = false;
    function _applyTranslations() {
        if (isTranslating) return;
        isTranslating = true;
        try {
            /* textContent */
            document.querySelectorAll('[data-i18n]').forEach(function (el) {
                const key = el.getAttribute('data-i18n');
                const val = window.t(key);
                if (val !== undefined && el.textContent !== val) el.textContent = val;
            });
            /* placeholder */
            document.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
                const key = el.getAttribute('data-i18n-ph');
                const val = window.t(key);
                if (val !== undefined && el.placeholder !== val) el.placeholder = val;
            });
            /* title / tooltip */
            document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
                const key = el.getAttribute('data-i18n-title');
                const val = window.t(key);
                if (val !== undefined && el.title !== val) el.title = val;
            });
            /* innerHTML (for <br> in buttons) */
            document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
                const key = el.getAttribute('data-i18n-html');
                const val = window.t(key);
                if (val !== undefined) {
                    const formatted = val.replace(/\n/g, '<br>');
                    if (el.innerHTML !== formatted) el.innerHTML = formatted;
                }
            });
        } finally {
            isTranslating = false;
        }
    }

    function _refreshLangButtons() {
        // Cập nhật emoji cờ và tooltip cho nút toggle mới
        const flagEl = document.getElementById('ts-lang-flag');
        if (flagEl) {
            flagEl.textContent = window.currentLang === 'vi' ? '🇻🇳' : '🇬🇧';
        }
        const toggleBtn = document.getElementById('ts-lang-toggle-btn');
        if (toggleBtn) {
            toggleBtn.title = window.currentLang === 'vi' ? 'Switch to English' : 'Chuyển sang Tiếng Việt';
        }

        const active = 'ts-lang-active';
        const inactive = 'ts-lang-inactive';
        ['vi', 'en'].forEach(function (code) {
            const btn = document.getElementById('lang-btn-' + code);
            if (!btn) return;
            btn.classList.toggle(active, code === window.currentLang);
            btn.classList.toggle(inactive, code !== window.currentLang);
        });
    }

    function _applyAll() {
        _applyTranslations();
        _refreshLangButtons();
        window.dispatchEvent(new CustomEvent('ts-lang-changed', { detail: { lang: window.currentLang } }));
    }

    // Unified Premium Date Formatting Helper
    window.formatDateTime = function (dateVal) {
        if (!dateVal) return '';
        let d;
        if (dateVal instanceof Date) {
            d = dateVal;
        } else if (typeof dateVal === 'number') {
            d = new Date(dateVal);
        } else if (typeof dateVal === 'string') {
            // Strip any trailing Z or offset if needed, or if it is a pure digit string
            if (/^\d+$/.test(dateVal)) {
                d = new Date(parseInt(dateVal));
            } else {
                d = new Date(dateVal);
            }
        } else {
            return '';
        }

        if (isNaN(d.getTime())) return '';

        const pad = (n) => n.toString().padStart(2, '0');
        const hh = pad(d.getHours());
        const mm = pad(d.getMinutes());
        const DD = pad(d.getDate());
        const MM = pad(d.getMonth() + 1);
        const YYYY = d.getFullYear();

        if (window.currentLang === 'vi') {
            return `${hh}:${mm} ${DD}/${MM}/${YYYY}`;
        } else {
            return `${MM}/${DD}/${YYYY}, ${hh}:${mm}`;
        }
    };

    /* ══════════════════════════════════════════════════════
       BOOT
    ══════════════════════════════════════════════════════ */
    document.addEventListener('DOMContentLoaded', function () {
        _applyAll();
        _applyTheme();

        /* Dynamic Event Delegation for Overlapping Flag Stack clicks */
        document.addEventListener('click', function (e) {
            const stack = e.target.closest('.ts-flag-stack');
            if (stack) {
                e.preventDefault();
                e.stopPropagation();
                window.toggleLang();
            }
        });

        /* Close panel when clicking outside */
        document.addEventListener('click', function (e) {
            const panel = document.getElementById('ts-settings-panel');
            const btn = document.getElementById('ts-settings-btn');
            const icon = document.getElementById('ts-settings-icon');
            if (!panel || panel.classList.contains('ts-panel-hidden')) return;
            if (!panel.contains(e.target) && btn && !btn.contains(e.target)) {
                panel.classList.add('ts-panel-hidden');
                if (icon) icon.style.transform = 'rotate(0deg)';
            }
        });

        /* Real-time language and theme sync across tabs */
        window.addEventListener('storage', function (e) {
            if (e.key === LANG_KEY) {
                window.currentLang = e.newValue || 'vi';
                _applyAll();
            }
            if (e.key === THEME_KEY) {
                window.currentTheme = e.newValue || 'dark';
                _applyTheme();
            }
        });

        /* Automatic Translation Observer for Dynamic DOM insertions (e.g. Alpine.js templates) */
        const observer = new MutationObserver(function (mutations) {
            let shouldReapply = false;
            mutations.forEach(function (mutation) {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function (node) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.getAttribute('data-i18n') ||
                                node.getAttribute('data-i18n-ph') ||
                                node.getAttribute('data-i18n-title') ||
                                node.getAttribute('data-i18n-html') ||
                                node.querySelector('[data-i18n], [data-i18n-ph], [data-i18n-title], [data-i18n-html]')
                            ) {
                                shouldReapply = true;
                            }
                        }
                    });
                }
            });
            if (shouldReapply) {
                _applyTranslations();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });

    /* ══════════════════════════════════════════════════════
       SHARED CSS (injected once)
    ══════════════════════════════════════════════════════ */
    const style = document.createElement('style');
    style.textContent = `
        @keyframes sidebarFadeDown {
            from {
                opacity: 0;
                transform: translateY(-24px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-sidebar-fade {
            animation: sidebarFadeDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        :root, html.dark {
            --bg-background: #0f172a; /* Slate 900 */
            --bg-surface: #1e293b; /* Slate 800 */
            --bg-surface-container: #1e293b;
            --bg-surface-container-high: #334155;
            --bg-surface-container-highest: #475569;
            --bg-surface-container-low: #0f172a;
            --bg-surface-container-lowest: #020617;
            --text-on-background: #f8fafc; /* Slate 50 */
            --text-on-surface: #f1f5f9; /* Slate 100 */
            --text-on-surface-variant: #94a3b8; /* Slate 400 */
            --color-primary-fixed: #eab308; /* Yellow 500 (Gold) */
            --color-primary-fixed-dim: #ca8a04; /* Yellow 600 */
            --color-on-primary-fixed: #000000; /* Black text */
            --border-outline-variant: #334155; /* Slate 700 */
            --border-outline: #475569; /* Slate 600 */
            --color-error: #ef4444; /* Red 500 */
        }

        html.light {
            --bg-background: #f4f5f7;
            --bg-surface: #ffffff;
            --bg-surface-container: #ffffff;
            --bg-surface-container-high: #ffffff;
            --bg-surface-container-highest: #ffffff;
            --bg-surface-container-low: #ffffff;
            --bg-surface-container-lowest: #ffffff;
            --text-on-background: #0f172a;
            --text-on-surface: #0f172a;
            --text-on-surface-variant: #162061;
            --color-primary-fixed: #162061;
            --color-primary-fixed-dim: #0f174a;
            --color-on-primary-fixed: #ffffff;
            --border-outline-variant: #e2e8f0;
            --border-outline: #cbd5e1;
            --color-error: #ba1a1a;
        }

        #ts-theme-btn, #ts-settings-btn {
            width: 37px;
            height: 37px;
            padding: 0;
            border-radius: 12px;
            background: rgba(49,53,60,0.25);
            border: 1px solid rgba(77,71,50,0.4);
            color: #d0c6ab;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.25s, color 0.25s, transform 0.25s;
            flex-shrink: 0;
        }
        #ts-theme-btn:hover, #ts-settings-btn:hover {
            background: rgba(49,53,60,0.55);
            color: #ffe16d;
            transform: scale(1.08);
        }
        #ts-theme-icon, #ts-settings-icon {
            font-size: 21px;
            transition: transform 0.45s cubic-bezier(.4,0,.2,1);
        }
        #ts-lang-toggle-btn {
            padding: 7px 10px;
            border-radius: 12px;
            background: rgba(49,53,60,0.25);
            border: 1px solid rgba(77,71,50,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.25s, transform 0.25s;
            flex-shrink: 0;
            font-size: 19px;
            line-height: 1;
        }
        #ts-lang-toggle-btn:hover {
            background: rgba(49,53,60,0.55);
            transform: scale(1.08);
        }
        #ts-settings-panel {
            position: absolute;
            top: calc(100% + 8px);
            left: 0;
            right: 0;
            background: #1c2026;
            border: 1px solid rgba(77,71,50,0.45);
            border-radius: 16px;
            padding: 16px;
            z-index: 200;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            transform-origin: top center;
            transition: opacity 0.22s ease, transform 0.22s ease;
            opacity: 1;
            transform: scaleY(1);
        }
        #ts-settings-panel.ts-panel-hidden {
            opacity: 0;
            transform: scaleY(0.85);
            pointer-events: none;
        }
        .ts-lang-label {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #d0c6ab;
            margin-bottom: 10px;
        }
        .ts-lang-row { display: flex; gap: 8px; }
        .ts-lang-btn {
            flex: 1;
            padding: 8px 10px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            border: 1px solid;
            cursor: pointer;
            transition: background 0.2s, color 0.2s, border-color 0.2s;
            text-align: center;
            font-family: 'Inter', sans-serif;
        }
        .ts-lang-active  { background: rgba(255,225,109,0.15); color: #ffe16d; border-color: rgba(255,225,109,0.4); }
        .ts-lang-inactive{ background: transparent; color: #d0c6ab; border-color: rgba(77,71,50,0.5); }
        .ts-lang-btn:hover { background: rgba(255,225,109,0.08); color: #ffe16d; border-color: rgba(255,225,109,0.3); }
        
        /* Premium Flag Buttons Style with Layered Stack & Opacity Overlap */
        .ts-flag-stack {
            position: relative;
            width: 48px;
            height: 32px;
            display: inline-block;
            cursor: pointer;
        }
        .ts-flag-btn {
            position: absolute;
            top: 0;
            left: 0;
            padding: 5px 7px;
            border-radius: 8px;
            background: rgba(49, 53, 60, 0.15);
            border: 1px solid rgba(77, 71, 50, 0.3);
            cursor: pointer;
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), 
                        opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), 
                        z-index 0.4s ease, 
                        background 0.25s, 
                        border-color 0.25s, 
                        box-shadow 0.25s;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .ts-flag-btn.ts-lang-active {
            z-index: 10;
            opacity: 1;
            transform: translate(0, 0) scale(1);
            background: rgba(255, 225, 109, 0.15);
            border-color: rgba(255, 225, 109, 0.6);
            box-shadow: 0 4px 12px rgba(255, 225, 109, 0.3);
        }
        .ts-flag-btn.ts-lang-inactive {
            z-index: 5;
            opacity: 0.25;
            transform: translate(6px, 4px) scale(0.92);
            background: rgba(49, 53, 60, 0.1);
            border-color: rgba(77, 71, 50, 0.2);
            box-shadow: none;
        }
        .ts-flag-stack:hover .ts-flag-btn.ts-lang-active {
            transform: translate(-2px, -2px) scale(1.02);
            border-color: rgba(255, 225, 109, 0.8);
            box-shadow: 0 6px 16px rgba(255, 225, 109, 0.4);
        }
        .ts-flag-stack:hover .ts-flag-btn.ts-lang-inactive {
            transform: translate(8px, 6px) scale(0.95);
            opacity: 0.75;
            background: rgba(49, 53, 60, 0.3);
            border-color: rgba(255, 225, 109, 0.35);
        }

        /* ══════════════════════════════════════════════════════
           LIGHT THEME OVERRIDES (Stunning & Premium)
        ══════════════════════════════════════════════════════ */
        html.light #ts-theme-btn, html.light #ts-settings-btn {
            background: rgba(22, 32, 97, 0.05);
            border: 1px solid rgba(22, 32, 97, 0.15);
            color: #162061;
        }
        html.light #ts-theme-btn:hover, html.light #ts-settings-btn:hover {
            background: rgba(22, 32, 97, 0.15);
            color: #162061;
        }
        html.light #ts-settings-panel {
            background: #ffffff;
            border: 1px solid rgba(22, 32, 97, 0.15);
            box-shadow: 0 10px 40px rgba(22, 32, 97, 0.1);
        }
        html.light .ts-lang-label {
            color: #162061;
        }
        html.light .ts-lang-active {
            background: rgba(22, 32, 97, 0.15);
            color: #162061;
            border-color: rgba(22, 32, 97, 0.3);
        }
        html.light .ts-lang-inactive {
            background: transparent;
            color: #162061;
            opacity: 0.65;
            border-color: rgba(22, 32, 97, 0.15);
        }
        html.light .ts-lang-btn:hover {
            background: rgba(22, 32, 97, 0.08);
            color: #162061;
            border-color: rgba(22, 32, 97, 0.25);
        }

        /* Light mode direct overrides for hardcoded layouts */
        html.light body,
        html.light .bg-\\[\\#0a0e14\\],
        html.light .bg-\\[\\#0b0e14\\],
        html.light .bg-\\[\\#10141a\\],
        html.light .bg-\\[\\#0a0a0a\\],
        html.light .bg-surface-container-lowest,
        html.light .bg-surface-container-low\\/20 {
            background-color: #f4f5f7 !important;
        }

        /* Dark surface containers → white/light in light mode */
        html.light .bg-surface,
        html.light .bg-surface\\/40,
        html.light .bg-surface\\/50,
        html.light .bg-surface\\/60,
        html.light .bg-surface-container,
        html.light .bg-surface-container-low,
        html.light .bg-surface-container-high,
        html.light .bg-surface-variant,
        html.light .bg-surface-container-highest,
        html.light .bg-surface-variant\\/10,
        html.light .bg-surface-variant\\/30,
        html.light .bg-surface-variant\\/40,
        html.light .bg-surface-variant\\/50,
        html.light .bg-surface-variant\\/60,
        html.light .bg-surface-container-high\\/80 {
            background-color: #ffffff !important;
        }
        html.light .bg-\\[\\#1c2026\\],
        html.light .bg-\\[\\#262a31\\],
        html.light .bg-\\[\\#31353c\\],
        html.light .bg-\\[\\#353940\\],
        html.light .bg-\\[\\#171717\\],
        html.light .bg-\\[\\#262626\\],
        html.light .bg-\\[\\#525252\\],
        html.light .bg-\\[\\#0c0f14\\],
        html.light .bg-\\[\\#525252\\]\\/40,
        html.light .bg-\\[\\#525252\\]\\/60,
        html.light .bg-\\[\\#262626\\]\\/60,
        html.light .bg-\\[\\#262626\\]\\/30,
        html.light .bg-\\[\\#000000\\]\\/95,
        html.light .bg-\\[\\#0a0a0a\\]\\/95 {
            background-color: #ffffff !important;
        }

        /* Dark gradient fade overlays → light in light mode */
        html.light .bg-gradient-to-t.from-background,
        html.light [class*="from-background"] {
            background: linear-gradient(to top, #f4f5f7, transparent) !important;
        }

        html.light aside {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-right-color: rgba(0, 0, 0, 0.08) !important;
        }
        html.light aside h1 {
            color: #162061 !important;
        }
        html.light aside p {
            color: #162061 !important;
            opacity: 0.65;
        }
        html.light aside a:not(.text-primary-fixed) {
            color: #162061 !important;
            opacity: 0.7;
        }
        html.light aside a:not(.text-primary-fixed):hover {
            background-color: rgba(22, 32, 97, 0.06) !important;
            color: #162061 !important;
            opacity: 1;
        }
        html.light aside a.text-primary-fixed {
            background: #162061 !important;
            color: #ffffff !important;
            border-left-color: #162061 !important;
            opacity: 1 !important;
            background-image: none !important;
        }
        html.light aside a.text-primary-fixed span {
            color: #ffffff !important;
        }
        html.light aside .mt-auto {
            background-color: rgba(0, 0, 0, 0.03) !important;
            border-color: rgba(0, 0, 0, 0.08) !important;
        }
        html.light aside .mt-auto p {
            color: #0f172a !important;
        }
        html.light aside .mt-auto span {
            color: #162061 !important;
        }

        /* Glass panels */
        html.light .glass-panel,
        html.light .bg-\\[\\#161b22\\]\\/60,
        html.light .bg-\\[\\#1c2026\\]\\/20,
        html.light .bg-\\[\\#0a0a0a\\]\\/60,
        html.light .bg-\\[\\#171717\\]\\/60,
        html.light .bg-\\[\\#0c0f13\\]\\/60,
        html.light .bg-surface-variant\\/10,
        html.light .bg-surface-variant\\/30,
        html.light .bg-white\\/\\[0\\.03\\],
        html.light .bg-white\\/5 {
            background-color: rgba(255, 255, 255, 0.85) !important;
            border-color: rgba(0, 0, 0, 0.08) !important;
            
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02) !important;
        }

        /* Inputs */
        html.light input[type="text"]:not(.ts-search),
        html.light input[type="password"],
        html.light input[type="email"],
        html.light input[type="date"],
        html.light textarea,
        html.light select,
        html.light div[contenteditable="true"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            color-scheme: light !important;
        }

        /* Text colors */
        html.light .text-white,
        html.light .text-on-surface,
        html.light .text-on-background,
        html.light .text-on-surface-variant,
        html.light h1:not(.text-primary-fixed),
        html.light h2:not(.text-primary-fixed),
        html.light h3:not(.text-primary-fixed),
        html.light h4:not(.text-primary-fixed),
        html.light p,
        html.light span:not(.material-symbols-outlined):not(.text-primary-fixed):not(.text-white) {
            color: #1e293b;
        }

        /* Accent text to Navy Blue */
        html.light .text-primary-fixed,
        html.light .text-primary-fixed-dim,
        html.light .text-\\[\\#ffd700\\],
        html.light .text-\\[\\#ffe16d\\],
        html.light .group-hover\\:text-\\[\\#ffd700\\]:hover,
        html.light .hover\\:text-\\[\\#ffd700\\]:hover {
            color: #162061 !important;
        }

        html.light .material-symbols-outlined.text-primary-fixed,
        html.light .material-symbols-outlined.text-\\[\\#ffd700\\] {
            color: #162061 !important;
        }

        /* Muted white text classes → Navy blue in light mode */
        html.light .text-white\/30,
        html.light .text-white\/40,
        html.light .text-white\/50,
        html.light .text-white\/60,
        html.light .text-white\/70,
        html.light .text-white\/80,
        html.light .text-on-surface-variant\/70,
        html.light .text-on-surface-variant\/50,
        html.light .text-on-surface-variant\/30 {
            color: #162061 !important;
            opacity: 0.65 !important;
        }

        /* Gray / slate text → Navy blue in light mode */
        html.light .text-gray-400,
        html.light .text-gray-500,
        html.light .text-gray-600,
        html.light .text-slate-400,
        html.light .text-slate-500,
        html.light .text-slate-600,
        html.light .text-\[\#7a7d81\],
        html.light .text-\[\#999077\],
        html.light .text-\[\#d0c6ab\],
        html.light .text-\[\#8a92a5\],
        html.light .text-\[\#808f9d\],
        html.light .text-on-surface-variant {
            color: #162061 !important;
            opacity: 0.75 !important;
        }

        /* Sidebar secondary texts (tagline, descriptions) */
        html.light aside p,
        html.light aside .font-label-sm,
        html.light .text-label-sm,
        html.light [class*="text-on-surface-variant"],
        html.light [class*="text-gray"],
        html.light [class*="text-slate"] {
            color: #162061 !important;
            opacity: 0.72 !important;
        }

        /* Override explicit opacity-60 / opacity-80 on nav links to keep readability */
        html.light aside a.opacity-60 {
            opacity: 0.65 !important;
            color: #162061 !important;
        }

        /* Buttons overrides: #162061 with white text */
        html.light button.bg-\\[\\#ffd700\\],
        html.light button.bg-primary-fixed,
        html.light button.bg-primary-fixed-dim,
        html.light button.bg-white,
        html.light a.bg-\\[\\#ffd700\\],
        html.light button\\[type\\=\\"submit\\"\\] {
            background-color: #162061 !important;
            color: #ffffff !important;
        }
        html.light button.bg-\\[\\#ffd700\\]:hover,
        html.light button.bg-primary-fixed:hover,
        html.light button.bg-primary-fixed-dim:hover,
        html.light button.bg-white:hover,
        html.light a.bg-\\[\\#ffd700\\]:hover,
        html.light button\\[type\\=\\"submit\\"\\]:hover {
            background-color: #0f174a !important;
            color: #ffffff !important;
        }
        html.light button.bg-\\[\\#ffd700\\] *,
        html.light button.bg-primary-fixed *,
        html.light button.bg-primary-fixed-dim * {
            color: #ffffff !important;
        }

        /* Border overrides */
        html.light .border-white\\/5,
        html.light .border-white\\/10,
        html.light .border-white\\/20,
        html.light .border-\\[\\#31353c\\]\\/30,
        html.light .border-\\[\\#31353c\\]\\/20,
        html.light .border-outline-variant\\/30,
        html.light .border-outline-variant {
            border-color: rgba(0, 0, 0, 0.08) !important;
        }

        /* Hover backgrounds */
        html.light .hover\\:bg-white\\/5:hover,
        html.light .hover\\:bg-white\\/10:hover,
        html.light .hover\\:bg-\\[\\#31353c\\]\\/40:hover,
        html.light .hover\\:bg-\\[\\#1c2026\\]\\/40:hover,
        html.light .hover\\:bg-surface-variant\\/40:hover {
            background-color: rgba(0, 0, 0, 0.04) !important;
        }

        /* Inputs */
        html.light input\\[type\\=\\"text\\"\\]:not(.ts-search),
        html.light input\\[type\\=\\"password\\"\\],
        html.light input\\[type\\=\\"email\\"\\],
        html.light input\\[type\\=\\"date\\"\\],
        html.light textarea,
        html.light select,
        html.light div\\[contenteditable\\=\\"true\\"\\] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            color-scheme: light !important;
        }
        html.light input\\[type\\=\\"text\\"\\]::placeholder,
        html.light textarea::placeholder,
        html.light div\\[contenteditable\\=\\"true\\"\\]::placeholder {
            color: rgba(22, 32, 97, 0.4) !important;
        }

        /* Diary scrollbars and trees & general hovers */
        html.light .hover\\:bg-\\[\\#1c2026\\]\\/40:hover,
        html.light .hover\\:bg-surface-variant\\/40:hover,
        html.light .hover\\:bg-surface-variant\\/50:hover,
        html.light .hover\\:bg-surface-variant\\/60:hover {
            background-color: rgba(0, 0, 0, 0.04) !important;
        }
        html.light .bg-primary-fixed\\/5 {
            background-color: rgba(22, 32, 97, 0.05) !important;
        }
        html.light .bg-primary-fixed\\/10 {
            background-color: rgba(22, 32, 97, 0.1) !important;
        }
        html.light .border-primary-fixed\\/20 {
            border-color: rgba(22, 32, 97, 0.2) !important;
        }
        html.light #obsidian-graph {
            background-color: #ffffff !important;
            border-color: rgba(0, 0, 0, 0.08) !important;
        }
        html.light .bg-\\[\\#0a0e14\\]\\/95 {
            background-color: rgba(244, 245, 247, 0.95) !important;
        }
        html.light header,
        html.light .border-b,
        html.light .border-t {
            border-color: rgba(0, 0, 0, 0.08) !important;
        }

        /* User chat bubbles (Coach page) */
        .ts-user-chat-bubble {
            background-color: #262a31 !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }
        html.light .ts-user-chat-bubble {
            background-color: #162061 !important;
            border-color: rgba(22, 32, 97, 0.4) !important;
        }
        html.light .ts-user-chat-bubble p,
        html.light .ts-user-chat-bubble span:not(.material-symbols-outlined) {
            color: #ffffff !important;
        }

        /* Premium Floating Switcher Tab Bar styling - Universal overrides */
        .ts-mobile-nav {
            background-color: rgba(15, 23, 42, 0.9) !important; /* Slate 900 */
            border: 1px solid rgba(251, 191, 36, 0.3) !important; /* Gold */
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
            
        }
        
        .ts-mobile-nav button.text-on-primary-fixed,
        .ts-mobile-nav button.text-on-primary-fixed span {
            color: #000000 !important; /* Premium high-contrast black text on gold gradient */
        }

        .ts-mobile-nav button:not(.text-on-primary-fixed),
        .ts-mobile-nav button:not(.text-on-primary-fixed) span {
            color: #94a3b8 !important; /* Slate 400 */
        }
        
        .ts-mobile-nav button:not(.text-on-primary-fixed):hover,
        .ts-mobile-nav button:not(.text-on-primary-fixed):hover span {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.08) !important;
        }

        /* Light Mode overrides for premium contrast and legibility */
        html.light .ts-mobile-nav {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-color: rgba(22, 32, 97, 0.15) !important;
            box-shadow: 0 8px 32px rgba(22, 32, 97, 0.12) !important;
        }

        html.light .ts-mobile-nav button.text-on-primary-fixed,
        html.light .ts-mobile-nav button.text-on-primary-fixed span {
            color: #ffffff !important; /* Perfect contrast: White text on dark navy gradient */
        }

        html.light .ts-mobile-nav button:not(.text-on-primary-fixed),
        html.light .ts-mobile-nav button:not(.text-on-primary-fixed) span {
            color: rgba(22, 32, 97, 0.6) !important; /* Slate/Navy Blue */
        }

        html.light .ts-mobile-nav button:not(.text-on-primary-fixed):hover,
        html.light .ts-mobile-nav button:not(.text-on-primary-fixed):hover span {
            color: rgba(22, 32, 97, 1) !important;
            background-color: rgba(22, 32, 97, 0.05) !important;
        }

        \.ts-lang-dropdown-btn {
            padding: 0 8px;
            height: 37px;
            border-radius: 12px;
            background: rgba(49,53,60,0.25);
            border: 1px solid rgba(77,71,50,0.4);
            color: #d0c6ab;
            cursor: pointer;
            transition: background 0.25s, color 0.25s, transform 0.25s;
        }
        .ts-lang-dropdown-btn:hover {
            background: rgba(49,53,60,0.55);
            color: #ffe16d;
        }
        .ts-lang-dropdown-menu {
            background: #1c2026;
            border: 1px solid rgba(77,71,50,0.45);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            padding: 4px;
        }
        .ts-lang-dropdown-item {
            color: #d0c6ab;
            transition: all 0.2s;
            border-radius: 8px;
        }
        .ts-lang-dropdown-item:hover {
            background: rgba(255,225,109,0.08);
            color: #ffe16d;
        }
        .ts-lang-dropdown-item.ts-lang-active {
            background: rgba(255,225,109,0.15);
            color: #ffe16d;
        }

        html.light .ts-lang-dropdown-btn {
            background: rgba(22, 32, 97, 0.05);
            border: 1px solid rgba(22, 32, 97, 0.15);
            color: #162061;
        }
        html.light .ts-lang-dropdown-btn:hover {
            background: rgba(22, 32, 97, 0.15);
            color: #162061;
        }
        html.light .ts-lang-dropdown-menu {
            background: #ffffff;
            border: 1px solid rgba(22, 32, 97, 0.15);
            box-shadow: 0 10px 40px rgba(22, 32, 97, 0.1);
        }
        html.light .ts-lang-dropdown-item {
            color: #162061;
        }
        html.light .ts-lang-dropdown-item:hover {
            background: rgba(22, 32, 97, 0.08);
            color: #0f174a;
        }
        html.light .ts-lang-dropdown-item.ts-lang-active {
            background: rgba(22, 32, 97, 0.15);
            color: #0f174a;
        }
    `;
    document.head.appendChild(style);

    /* ══════════════════════════════════════════════════════
       GLOBAL VALIDATION OVERRIDES
    ══════════════════════════════════════════════════════ */
    document.addEventListener('invalid', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            if (e.target.validity.valueMissing) {
                e.target.setCustomValidity(window.t('login.msg_required'));
            } else if (e.target.validity.typeMismatch && e.target.type === 'email') {
                e.target.setCustomValidity(window.t('login.msg_email_invalid'));
            }
        }
    }, true);

    document.addEventListener('input', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            e.target.setCustomValidity('');
        }
    }, true);

    // Global fetch interceptor to automatically route /api/v1 calls to the remote backend
    // when running frontend locally (e.g. file:///... or localhost) pointing to the deployed server.
    (function () {
        const originalFetch = window.fetch;
        window.fetch = function (input, init) {
            if (typeof input === 'string' && input.startsWith('/api/v1')) {
                let apiBase = localStorage.getItem('thapsang_api_base');
                if (!apiBase) {
                    if (window.location.protocol === 'file:') {
                        apiBase = 'https://thapsang.mojo.vn';
                    } else {
                        apiBase = window.location.origin;
                    }
                }
                apiBase = apiBase.replace(/\/$/, '');
                input = apiBase + input;
            }
            return originalFetch(input, init);
        };
    })();
})();
