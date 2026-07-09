// cache-manager.js
// Quản lý Native HTTP Caching (Stale-While-Revalidate)

const API_CACHE_NAME = 'thapsang-api-cache-v1';

document.addEventListener('DOMContentLoaded', () => {
    enableFetchCaching();
});

function enableFetchCaching() {
    // Lưu lại hàm fetch gốc
    const originalFetch = window.fetch;

    window.fetch = async function(...args) {
        let request;
        if (args[0] instanceof Request) {
            request = args[0];
        } else {
            request = new Request(args[0], args[1]);
        }

        // Chỉ cache các request GET
        if (request.method !== 'GET') {
            return originalFetch.apply(this, args);
        }

        // Bỏ qua nếu là request file cache-manager.js để tránh vòng lặp hoặc cache chính nó
        if (request.url.includes('cache-manager.js')) {
            return originalFetch.apply(this, args);
        }

        // Bỏ qua các API liên quan đến tasks hoặc db/chats để tránh lưu đệm/cache
        if (request.url.includes('/api/v1/tasks') || request.url.includes('/api/v1/db/chats')) {
            return originalFetch.apply(this, args);
        }

        try {
            const cache = await caches.open(API_CACHE_NAME);
            const cachedResponse = await cache.match(request);
            
            // Nếu có dữ liệu trong cache -> Trả về ngay lập tức để tăng tốc độ load
            if (cachedResponse) {
                // Background fetch để lấy dữ liệu mới nhất (Stale-While-Revalidate)
                // Phải clone request vì request chỉ được dùng 1 lần
                originalFetch(request.clone()).then(response => {
                    // Cập nhật lại cache nếu fetch thành công
                    if (response.ok) {
                        cache.put(request.clone(), response.clone());
                        
                        // Dispatch event để UI biết có dữ liệu mới (nếu UI cần update realtime)
                        window.dispatchEvent(new CustomEvent('cache-revalidated', { 
                            detail: { url: request.url } 
                        }));
                    }
                }).catch(err => {
                    console.warn('Background revalidation failed:', err);
                });

                // Trả về dữ liệu cũ trước (cực kỳ nhanh)
                return cachedResponse.clone();
            }
            
            // Nếu chưa có trong cache -> fetch thực tế và lưu vào cache
            const response = await originalFetch(request.clone());
            if (response.ok) {
                cache.put(request.clone(), response.clone());
            }
            return response;
            
        } catch (error) {
            console.error('Lỗi Cache API:', error);
            // Fallback: nếu lỗi cache API thì gọi thẳng lên server
            return originalFetch.apply(this, args);
        }
    };
}
