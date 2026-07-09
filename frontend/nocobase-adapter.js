
(function() {
    const urlMapping = {
    "/api/v1/cohort": {
        "GET": "/api/v1/cohort:list"
    },
    "/api/v1/cohort/join": {
        "POST": "/api/v1/cohort:join"
    },
    "/api/v1/cohort/personalize-week": {
        "POST": "/api/v1/cohort:personalize_week"
    },
    "/api/v1/cohort/check-context": {
        "GET": "/api/v1/cohort:check_context"
    },
    "/api/v1/cohort/members": {
        "GET": "/api/v1/cohort:members"
    },
    "/api/v1/cohort/syllabus": {
        "GET": "/api/v1/cohort:syllabus"
    },
    "/api/v1/cohort/activity": {
        "GET": "/api/v1/cohort:activity"
    },
    "/api/v1/cohort/member-progress": {
        "POST": "/api/v1/cohort:member_progress"
    },
    "/api/v1/cohort/update-progress": {
        "POST": "/api/v1/cohort:update_progress"
    },
    "/api/v1/cohort/ai-retrospective": {
        "GET": "/api/v1/cohort:ai_retrospective",
        "POST": "/api/v1/cohort:ai_retrospective"
    },
    "/api/v1/cohort/ai-bottleneck": {
        "POST": "/api/v1/cohort:ai_bottleneck"
    },
    "/api/v1/db/chats": {
        "GET": "/api/v1/db:chats",
        "POST": "/api/v1/db:chats"
    },
    "/api/v1/db/chats/{session_id}": {
        "DELETE": "/api/v1/db_chats:delete/{session_id}"
    },
    "/api/v1/db/aoa": {
        "GET": "/api/v1/db:aoa",
        "POST": "/api/v1/db:aoa"
    },
    "/api/v1/auth/login": {
        "POST": "/api/v1/auth:login"
    },
    "/api/v1/auth/profile/{username}": {
        "GET": "/api/v1/auth_profile:get/{username}",
        "POST": "/api/v1/auth_profile:post/{username}"
    },
    "/api/v1/auth/onboarding/{username}": {
        "POST": "/api/v1/auth_onboarding:post/{username}",
        "GET": "/api/v1/auth_onboarding:get/{username}"
    },
    "/api/v1/profile/{username}/context": {
        "GET": "/api/v1/profile:get/{username}/context"
    },
    "/api/v1/diary/generate": {
        "POST": "/api/v1/diary:generate"
    },
    "/api/v1/diary/{username}": {
        "GET": "/api/v1/diary:get/{username}",
        "POST": "/api/v1/diary:create/{username}"
    },
    "/api/v1/diary/{username}/{entry_id}": {
        "DELETE": "/api/v1/diary:destroy/{username}/{entry_id}"
    },
    "/api/v1/diary/{username}/folders": {
        "GET": "/api/v1/diary:get/{username}/folders",
        "POST": "/api/v1/diary:create/{username}/folders"
    },
    "/api/v1/diary/{username}/folders/{folder_name}": {
        "DELETE": "/api/v1/diary_{username}:delete/folders/{folder_name}"
    },
    "/api/v1/auth/request-otp": {
        "POST": "/api/v1/auth:request_otp"
    },
    "/api/v1/auth/register": {
        "POST": "/api/v1/auth:register"
    },
    "/api/v1/auth/forgot-password/request-otp": {
        "POST": "/api/v1/auth:forgot_password_request_otp"
    },
    "/api/v1/auth/forgot-password/reset": {
        "POST": "/api/v1/auth:forgot_password_reset"
    },
    "/api/v1/profile/{username}/stats": {
        "GET": "/api/v1/profile:get/{username}/stats"
    },
    "/api/v1/profile/{username}/mindset": {
        "GET": "/api/v1/profile:get/{username}/mindset"
    },
    "/api/v1/aoa/posts": {
        "GET": "/api/v1/aoa:posts",
        "POST": "/api/v1/aoa:posts"
    },
    "/api/v1/aoa/posts/{post_id}/like": {
        "POST": "/api/v1/aoa_posts:post/{post_id}/like"
    },
    "/api/v1/aoa/posts/{post_id}/comment": {
        "POST": "/api/v1/aoa_posts:post/{post_id}/comment"
    },
    "/api/v1/aoa/posts/{post_id}/report": {
        "POST": "/api/v1/aoa_posts:post/{post_id}/report"
    },
    "/api/v1/aoa/posts/{post_id}": {
        "PATCH": "/api/v1/aoa_posts:patch/{post_id}",
        "DELETE": "/api/v1/aoa_posts:delete/{post_id}"
    },
    "/api/v1/aoa/posts/{post_id}/restore": {
        "POST": "/api/v1/aoa_posts:post/{post_id}/restore"
    },
    "/api/v1/aoa/posts/{post_id}/hide": {
        "POST": "/api/v1/aoa_posts:post/{post_id}/hide"
    },
    "/api/v1/aoa/posts/{post_id}/save": {
        "POST": "/api/v1/aoa_posts:post/{post_id}/save"
    },
    "/api/v1/aoa/trending": {
        "GET": "/api/v1/aoa:trending"
    },
    "/api/v1/aoa/posts/repost": {
        "POST": "/api/v1/aoa:posts_repost"
    },
    "/api/v1/cohorts": {
        "GET": "/api/v1/cohorts:list"
    },
    "/api/v1/chat/welcome": {
        "POST": "/api/v1/chat:welcome"
    },
    "/api/v1/chat": {
        "POST": "/api/v1/chat:create"
    },
    "/api/v1/chat/mindmap": {
        "POST": "/api/v1/chat:mindmap"
    },
    "/api/v1/cohort/tasks/{username}": {
        "GET": "/api/v1/cohort_tasks:get/{username}",
        "POST": "/api/v1/cohort_tasks:post/{username}"
    },
    "/api/v1/cohort/tasks/{task_id}": {
        "PATCH": "/api/v1/cohort_tasks:patch/{task_id}"
    },
    "/api/v1/cohort/generate-quiz": {
        "POST": "/api/v1/cohort:generate_quiz"
    },
    "/api/v1/cohort/submit-quiz": {
        "POST": "/api/v1/cohort:submit_quiz"
    },
    "/api/v1/voice/generate": {
        "POST": "/api/v1/voice:generate"
    },
    "/api/v1/voice/status": {
        "POST": "/api/v1/voice:status"
    },
    "/api/v1/tasks/generate-microsteps": {
        "POST": "/api/v1/tasks:generate_microsteps"
    },
    "/api/v1/tasks/{username}": {
        "GET": "/api/v1/tasks:get/{username}",
        "POST": "/api/v1/tasks:create/{username}"
    },
    "/api/v1/tasks/{task_id}": {
        "PATCH": "/api/v1/tasks:update/{task_id}",
        "DELETE": "/api/v1/tasks:destroy/{task_id}"
    }
};

    // 1. Unwrap JSON responses globally
    const originalJson = Response.prototype.json;
    Response.prototype.json = async function() {
        const data = await originalJson.call(this);
        // Only unwrap if it is EXACTLY {"data": ...} with no other keys
        if (data && typeof data === 'object' && data.data !== undefined && Object.keys(data).length === 1) {
            return data.data;
        }
        return data;
    };

    // 2. Intercept fetch
    const originalFetch = window.fetch;
    window.fetch = async function(input, init) {
        let url = typeof input === 'string' ? input : input.url;
        let method = (init && init.method) ? init.method.toUpperCase() : 'GET';

        if (url.includes('/api/v1/')) {
            // Attempt to match and replace based on mapping
            let matched = false;
            for (const [oldUrl, methods] of Object.entries(urlMapping)) {
                // Convert fastapi path template /api/v1/users/{id} to regex
                let regexPattern = oldUrl.replace(/\{.*?\}/g, '([^/]+)');
                let regex = new RegExp('^' + regexPattern + '(?:\\?.*)?$');
                
                let pathOnly;
                try {
                    pathOnly = new URL(url, window.location.origin).pathname;
                } catch(e) {
                    pathOnly = url.split('?')[0];
                }
                
                let match = pathOnly.match(regex);
                
                if (match) {
                    let newUrlTemplate = methods[method];
                    if (!newUrlTemplate && (method === 'GET' || method === 'POST')) {
                        // Fallback only if the endpoint doesn't have other methods that could match in later iterations
                        newUrlTemplate = methods['GET'] || methods['POST'];
                    }
                    if (newUrlTemplate) {
                        // Replace params
                        let newUrl = newUrlTemplate;
                        let paramMatches = oldUrl.match(/\{.*?\}/g);
                        if (paramMatches) {
                            paramMatches.forEach((param, index) => {
                                newUrl = newUrl.replace(param, match[index + 1]);
                            });
                        }
                        url = url.replace(pathOnly, newUrl);
                        matched = true;
                        break;
                    }
                }
            }
            
            // Fallback for dynamic urls if regex fails
            if (!matched) {
                let parts = url.split('/api/v1/')[1].split('/');
                if (parts.length > 0) {
                    let collection = parts[0];
                    let action = method === 'GET' ? 'list' : 'create';
                    url = url.replace(`/api/v1/${collection}`, `/api/v1/${collection}:${action}`);
                }
            }
        }

        // Wrap request body
        if (init && init.body && typeof init.body === 'string' && ['POST', 'PUT', 'PATCH'].includes(method)) {
            try {
                const parsed = JSON.parse(init.body);
                if (!parsed.data) {
                    init.body = JSON.stringify({ data: parsed });
                }
            } catch(e) {}
        }

        if (typeof input === 'string') {
            input = url;
        } else {
            input = new Request(url, input);
        }

        return originalFetch(input, init);
    };
})();
