from django.urls import path
from backend import views
from backend.views import FetchWorksView, FetchLikesView, FetchFavoritesView, FetchHotView, FetchFollowWorksView

urlpatterns = [
    path("", views.index, name="index"),
    path('register', views.register, name='register'),
    # User
    path('user/sendCode', views.send_code, name='send_code'),
    path('user/loginByCode', views.user_login_by_code, name='user_login_by_code'),
    path('user/loginByPassword', views.user_login_by_password, name='user_login_by_password'),
    path('user/updateProfile', views.user_update_profile, name='user_update_profile'),
    path('user/fetchProfile', views.user_fetch_profile, name='user_fetch_profile'),
    path('user/updateAvatar', views.user_update_avatar, name='user_update_avatar'),
    path('user/getAvatar', views.user_get_avatar, name='user_get_avatar'),
    path('user/getContacts',views.user_get_contacts, name='user_get_contacts'),
    path('user/contactRequest',views.user_contact_request, name='user_contact_request'),
    path('user/getMessages',views.user_get_messages, name='user_get_messages'),
    path('user/sendMessage',views.user_send_message, name='user_send_message'),
    path('user/updateBasicInfo', views.update_basic_info, name='update_basic_info'),
    # Announcement
    path('anno/add', views.announcement_add, name='announcement_add'),
    path('anno/update', views.announcement_update, name='announcement_update'),
    path('anno/delete', views.announcement_delete, name='announcement_delete'),
    path('anno/get', views.announcement_list, name='announcement_list'),
    path('user/fetchWorks', FetchWorksView.as_view(), name='user-fetch-works'),
    path('user/fetchLikes', FetchLikesView.as_view(), name='user-fetch-likes'),
    path('user/fetchFavorites', FetchFavoritesView.as_view(), name='user-fetch-Favorites'),
    path('user/fetchHot', FetchHotView.as_view(), name='user-fetch-hot'),
    path('user/fetchFollowWorks', FetchFollowWorksView.as_view(), name='user-fetch-follow-works'),

    # 更新密码
    path('user/updatePassword', views.user_update_password, name='user_update_password'),

    # knowledgeBase
    path("kb/create", views.create_kb, name='create_knowledgeBase'),
    path('kb/uploadText',   views.upload_kb_file, name='upload_kb_file'),
    path('kb/getTexts', views.get_kb_files, name='get_kb_texts'),
    path("kb/getTextContent", views.get_text_content, name='get_text_content'),
    path('rl/getKnowledgeBases', views.get_knowledge_bases, name='get_knowledge_bases'),
    path('kb/uploadPicture', views.upload_picture_kb_file, name='upload_picture_kb_file'),
    path('kb/getPictures', views.get_pictures, name='get_pictures'),
    path('kb/uploadTable', views.upload_table_kb_file, name='upload_table_kb_file'),
    path('kb/getTables', views.get_table_data, name='get_tables'),
    path('rl/delete', views.delete_resource, name='delete_resource'),
    path('rl/edit', views.edit_resource, name='edit_resource'),
    path('kb/deletePicture', views.delete_picture, name='delete_picture'),
    path('kb/updatePicture', views.update_picture, name='update_picture'),
    path('kb/deleteText', views.delete_text, name='delete_text'),
    path('kb/updateTable', views.update_table, name='update_table'),
    path('kb/addTableRow', views.add_table_row, name='add_table_row'),
    path('kb/deleteTableRows', views.delete_table_rows, name='delete_table_rows'),
    path('kb/getTextTree',    views.get_text_tree,    name='get_text_tree'),

    # 工作流
    path('workflow/run',views.workflow_run, name='workflow_run'),
    path('workflow/create',views.workflow_create, name='workflow_create'),
    path('workflow/fetch',views.workflow_fetch, name='workflow_fetch'),
    path('workflow/save',views.workflow_save, name='workflow_save'),
    path('workflow/fetchAll',views.workflow_fetchAll, name='workflow_fetchAll'),
    path('workflow/delete',views.workflow_delete, name='workflow_delete'),
    path('workflow/runSingle',views.workflow_run_single, name='workflow_run_single'),

    # 审核
    path('sensitive/check', views.check_sensitive_words, name='check_sensitive_words'),
    path('sensitive/add', views.add_sensitive_word, name='add_sensitive_word'),
    path('sensitive/delete', views.delete_sensitive_word, name='delete_sensitive_word'),
    path('sensitive/list', views.list_sensitive_words, name='list_sensitive_words'),
    path('admin/fetchPendingAgents', views.fetch_pending_agents, name='fetch_pending_agents'),
    path('admin/reviewAgent', views.review_agent, name='review_agent'),
    path('admin/fetchUser', views.fetch_user, name='fetch_user'),
    path('admin/banUser',   views.ban_user,   name='ban_user'),
    path('admin/unbanUser', views.unban_user, name='unban_user'),
    path('admin/cntUserInfo', views.cnt_user_info, name='cnt_user_info'),

    #智能体
    path('agent/fetchAll',views.agent_fetch_all,name='agent_fetch_all'),
    path('agent/release',views.agent_release, name='agent_release'),
    path('agent/remove',views.agent_remove, name='agent_remove'),
    path('agent/delete',views.agent_delete, name='agent_delete'),
    path('agent/edit', views.edit_agent, name='edit_agent'),

    #社区
    path('community/agentFetchBasicInfo',views.community_agent_fetch_basic_info, name='community_agent_fetch_basic_info'),
    path('community/agentFetchUserActions',views.community_agent_fetch_user_actions, name='community_agent_fetch_user_actions'),
    path('community/agentFetchComments',views.community_agent_fetch_comments, name='community_agent_fetch_comments'),
    path('community/agentHandleLike',views.community_agent_handle_like, name='community_agent_handle_like'),
    path('community/agentHandleFavorite',views.community_agent_handle_Favorite, name='community_agent_handle_Favorite'),
    path('community/agentHandleFollow',views.community_agent_handle_Follow, name='community_agent_handle_Follow'),
    path('community/agentHandleCopy',views.community_agent_handle_copy, name='community_agent_handle_copy'),
    path('community/agentSendComment',views.community_agent_send_comment, name='community_agent_send_comment'),
    path('community/fetchAllAgents', views.fetch_all_published_agents, name='fetch_all_agents'),

]