from django.db import models
import uuid
from django.utils import timezone

# 1. 用户表（User）
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=100, unique=True)
    is_banned = models.BooleanField(default=False)  # 0-正常，1-封禁
    can_post = models.BooleanField(default=True)  # 0-无发布权限，1-可发布
    ban_expire = models.DateTimeField(null=True, blank=True)
    post_expire = models.DateTimeField(null=True, blank=True)
    fans_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    registered_at = models.DateTimeField(auto_now_add=True)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

# 2. 管理员表（Administrator）
class Administrator(models.Model):
    admin_id = models.AutoField(primary_key=True)
    account = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.account

# 3. 关注关系表（Follow Relationship）
class FollowRelationship(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followee = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follow_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followee')

    def __str__(self):
        return f"{self.follower.username} follows {self.followee.username}"

# 4. 私信表（Private Message）
class PrivateMessage(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Msg {self.message_id} from {self.sender.username} to {self.receiver.username}"

# 5. 管理员日志表（Admin Log）
class AdminLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    admin = models.ForeignKey(Administrator, on_delete=models.CASCADE)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=50)
    operation_time = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Log {self.log_id} by {self.admin.account}"

# 6. 敏感词表（Sensitive Words）
class SensitiveWord(models.Model):
    word_id = models.AutoField(primary_key=True)
    word_content = models.CharField(max_length=100, unique=True)
    replacement = models.CharField(max_length=100)

    def __str__(self):
        return self.word_content

# 7. 评论表（Comment）
# 由于评论中需要关联到智能体，因此在 Agent 模型定义之后再建立外键引用
class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    # agent 外键待 Agent 定义后关联（此处用字符串形式引用）
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.comment_id} by {self.user.username}"

# 8. 公告表（Announcement）
class Announcement(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    time = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.type})"

# 9. 工作流表（Workflow）
class Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    nodes = models.TextField()  # 存储 JSON 或其他格式数据
    edges = models.TextField()  # 存储 JSON 或其他格式数据
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建者
    is_builtin = models.BooleanField(default=False)  # 0-用户创建，1-系统内置
    view_points = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon_url = models.URLField(max_length=500, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Workflow {self.workflow_id}"

# 知识库表（Knowledge Base）
class KnowledgeBase(models.Model):
    kb_id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    kb_name = models.CharField(max_length=100, unique=True)
    kb_type = models.CharField(max_length=50)
    kb_description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 创建者
    icon = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.kb_name


class KnowledgeFile(models.Model):
    kb = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='knowledge/')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    SEGMENT_MODE_CHOICES = [
        ('auto', '自动分段'),
        ('custom', '自定义分段'),
        ('hierarchical', '按层级结构分段'),
    ]
    segment_mode = models.CharField(
        max_length=20,
        choices=SEGMENT_MODE_CHOICES,
        default='auto'
    )

    def __str__(self):
        return self.name

class KnowledgeChunk(models.Model):
    chunk_id = models.AutoField(primary_key=True)
    kb = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    file = models.ForeignKey('KnowledgeFile', on_delete=models.CASCADE)
    content = models.TextField()
    order = models.IntegerField(default=0)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)  # 层级结构支持
    created_at = models.DateTimeField(auto_now_add=True)
    embedding = models.TextField(null=True, blank=True)  # 存为 JSON 字符串

    def __str__(self):
        return f"Chunk {self.chunk_id} in KB {self.kb.kb_name}"

# 知识条目表（Agent 与 KB 的关联）
class AgentKnowledgeEntry(models.Model):
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE)
    kb = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)  # 0-未调用，1-已调用

    class Meta:
        unique_together = ('agent', 'kb')

    def __str__(self):
        return f"KnowledgeEntry: Agent {self.agent.agent_id} - KB {self.kb.kb_id}"

# 12. 智能体表（Agent）
class Agent(models.Model):
    STATUS_CHOICES = [
        ('private', '私有'),
        ('check', '待审核'),
        ('published', '已发布'),
    ]

    agent_id = models.AutoField(primary_key=True)
    agent_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    opening_line = models.CharField(max_length=255, null=True, blank=True)
    prompt = models.TextField(null=True, blank=True)
    persona = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50)
    likes_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    is_modifiable = models.BooleanField(default=True)  # 1-允许修改，0-不允许修改
    icon_url = models.URLField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agents')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='private')
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='agents')

    def __str__(self):
        return self.agent_name

# 13. 智能体工作流关系表（Agent-Workflow Relation）
class AgentWorkflowRelation(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('agent', 'workflow')

    def __str__(self):
        return f"Agent {self.agent.agent_id} - Workflow {self.workflow.workflow_id}"

# 14. 用户交互表（User Interaction）
class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)  # 0-未点赞，1-已点赞
    is_favorited = models.BooleanField(default=False)  # 0-未收藏，1-已收藏

    class Meta:
        unique_together = ('user', 'agent')

    def __str__(self):
        return f"UserInteraction: {self.user.username} - {self.agent.agent_name}"

# 15. 对话历史表（Dialogue History）
class DialogueHistory(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('agent', 'Agent'),
    )

    dialog_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    sender = models.CharField(max_length=5, choices=SENDER_CHOICES)
    conversation_content = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dialogue {self.dialog_id} ({self.sender})"

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    conversation = models.ForeignKey(Session, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField()  # True为用户消息，False为AI回复
    timestamp = models.DateTimeField(auto_now_add=True)
