import { mock } from "mockjs";

mock("/agent/getComments", "get", () => {
  return {
    code: 0,
    message: "获取成功",
    data: [
      {
        id: 1,
        name: "创意达人",
        userId: "@creative_master",
        avatar: "https://picsum.photos/40/40?random=4",
        content:
          "这个写作助手真的很棒！帮我完成了很多高质量的文章，特别是在优化文章结构方面非常专业。",
        time: "2024-03-15 14:30",
      },
      {
        id: 2,
        name: "科技探索者",
        userId: "@tech_explorer",
        avatar: "https://picsum.photos/40/40?random=5",
        content:
          "使用了一周，文章质量明显提升，特别是在专业术语的使用上很准确。",
        time: "2024-03-15 13:25",
      },
      {
        id: 3,
        name: "内容创作者",
        userId: "@content_creator",
        avatar: "https://picsum.photos/40/40?random=6",
        content:
          "界面简洁，操作方便，生成的内容很有创意，推荐给需要写作帮助的朋友们！",
        time: "2024-03-15 12:18",
      },
      {
        id: 4,
        name: "数据分析师",
        userId: "@data_analyst",
        avatar: "https://picsum.photos/40/40?random=7",
        content:
          "作为一个经常需要写报告的人，这个助手帮我节省了很多时间，而且质量很好。",
        time: "2024-03-15 11:45",
      },
      {
        id: 5,
        name: "营销专家",
        userId: "@marketing_pro",
        avatar: "https://picsum.photos/40/40?random=8",
        content: "文案创作必备工具，特别适合需要大量内容创作的营销人员。",
        time: "2024-03-15 10:30",
      },
      {
        id: 6,
        name: "学术研究者",
        userId: "@researcher",
        avatar: "https://picsum.photos/40/40?random=9",
        content: "学术写作方面表现出色，参考文献的引用格式也很规范。",
        time: "2024-03-15 09:20",
      },
      {
        id: 7,
        name: "自媒体人",
        userId: "@media_creator",
        avatar: "https://picsum.photos/40/40?random=10",
        content: "日常创作的得力助手，文章的逻辑性和可读性都很好。",
        time: "2024-03-14 23:15",
      },
      {
        id: 8,
        name: "编辑总监",
        userId: "@editor_chief",
        avatar: "https://picsum.photos/40/40?random=11",
        content:
          "作为专业编辑，我认为这个AI助手的输出质量很高，需要的修改很少。",
        time: "2024-03-14 22:40",
      },
      {
        id: 9,
        name: "写作爱好者",
        userId: "@writing_lover",
        avatar: "https://picsum.photos/40/40?random=12",
        content: "对新手很友好，会给出很多有建设性的修改建议。",
        time: "2024-03-14 21:55",
      },
      {
        id: 10,
        name: "产品经理",
        userId: "@product_manager",
        avatar: "https://picsum.photos/40/40?random=13",
        content: "产品文档写作的好帮手，专业术语运用准确，逻辑清晰。",
        time: "2024-03-14 20:30",
      },
      {
        id: 11,
        name: "技术博主",
        userId: "@tech_blogger",
        avatar: "https://picsum.photos/40/40?random=14",
        content: "技术文章写作效果很好，能够准确理解和表达技术概念。",
        time: "2024-03-14 19:15",
      },
      {
        id: 12,
        name: "教育工作者",
        userId: "@educator",
        avatar: "https://picsum.photos/40/40?random=15",
        content: "很适合用来辅助教案编写，生成的内容通俗易懂。",
        time: "2024-03-14 18:40",
      },
      {
        id: 13,
        name: "新闻记者",
        userId: "@journalist",
        avatar: "https://picsum.photos/40/40?random=16",
        content: "新闻写作的好助手，能快速整理要点，生成初稿。",
        time: "2024-03-14 17:25",
      },
      {
        id: 14,
        name: "小说作家",
        userId: "@novelist",
        avatar: "https://picsum.photos/40/40?random=17",
        content: "在创意写作方面表现出色，能给出很多有趣的故事发展建议。",
        time: "2024-03-14 16:10",
      },
      {
        id: 15,
        name: "广告文案",
        userId: "@copywriter",
        avatar: "https://picsum.photos/40/40?random=18",
        content: "文案创作效果很好，能抓住重点，文字简洁有力。",
        time: "2024-03-14 15:00",
      },
    ],
  };
});

mock("/agent/sendComment", "post", () => {
  return {
    code: 0,
    message: "评论成功",
  };
});

mock("/user/getContacts", "get", () => {
  return {
    code: 0,
    message: "获取成功",
    data: [
      {
        id: 1,
        name: "Joyful Mind",
        avatar: "https://picsum.photos/40/40?random=1",
        unread: 0,
        lastMessage: {
          text: "https://www.zhihu.com/q...",
          type: "assistant",
        },
        lastMessageTime: "1 小时前",
      },
      {
        id: 2,
        name: "AI实验室",
        avatar: "https://picsum.photos/40/40?random=2",
        unread: 1,
        lastMessage: {
          text: "亲爱的 Saisyc 我们有接单策...",
          type: "assistant",
        },
        lastMessageTime: "昨天 14:24",
      },
      {
        id: 3,
        name: "段超",
        avatar: "https://picsum.photos/40/40?random=3",
        unread: 0,
        lastMessage: {
          text: "[耶][耶][耶]",
          type: "user",
        },
        lastMessageTime: "04-04",
      },
      {
        id: 4,
        name: "史密斯",
        avatar: "https://picsum.photos/40/40?random=4",
        unread: 0,
        lastMessage: {
          text: "https://www.zhihu.com/q...",
          type: "assistant",
        },
        lastMessageTime: "04-03",
      },
      {
        id: 5,
        name: "Wille Zur Macht",
        avatar: "https://picsum.photos/40/40?random=5",
        unread: 0,
        lastMessage: {
          text: "https://www.zhihu.com/q...",
          type: "assistant",
        },
        lastMessageTime: "04-03",
      },
      {
        id: 6,
        name: "Nefelibata",
        avatar: "https://picsum.photos/40/40?random=6",
        unread: 0,
        lastMessage: {
          text: "https://www.zhihu.com/q...",
          type: "assistant",
        },
        lastMessageTime: "04-03",
      },
      {
        id: 7,
        name: "专喷民科和公知",
        avatar: "https://picsum.photos/40/40?random=7",
        unread: 0,
        lastMessage: {
          text: "https://www.zhihu.com/q...",
          type: "assistant",
        },
        lastMessageTime: "04-03",
      },
      {
        id: 8,
        name: "知乎知识付费小...",
        avatar: "https://picsum.photos/40/40?random=8",
        unread: 1,
        lastMessage: {
          text: "亲爱的Saisyc： 注意到你经...",
          type: "assistant",
        },
        lastMessageTime: "04-02",
      },
    ],
  };
});

const messageData = [
  [
    {
      type: "system",
      sender: "系统",
      avatar: "https://picsum.photos/40/40?random=9",
      time: "10:30",
      text: "欢迎使用知乎私信！有什么可以帮助您的？",
    },
    {
      type: "user",
      sender: "我",
      avatar: "https://picsum.photos/40/40?random=10",
      time: "10:31",
      text: "你好，我想了解一些关于人工智能的知识。",
    },
    {
      type: "assistant",
      sender: "Joyful Mind",
      avatar: "https://picsum.photos/40/40?random=1",
      time: "10:32",
      text: "您好！人工智能（AI）是计算机科学的一个分支，旨在创造能够模拟人类智能的机器。它包括学习、推理和自我修正等能力。您具体想了解哪方面的内容？",
    },
  ],
  [
    {
      type: "assistant",
      sender: "AI实验室",
      avatar: "https://picsum.photos/40/40?random=2",
      time: "14:24",
      text: "亲爱的 Saisyc，我们有接单策略和合作方案，您可以随时联系我们了解详情！",
    },
  ],
  [
    {
      type: "user",
      sender: "段超",
      avatar: "https://picsum.photos/40/40?random=3",
      time: "04-04",
      text: "[耶][耶][耶]",
    },
  ],
  [
    {
      type: "assistant",
      sender: "知乎知识付费小...",
      avatar: "https://picsum.photos/40/40?random=8",
      time: "04-02",
      text: "亲爱的 Saisyc：注意到您经常浏览知识付费相关内容，我们有专属优惠活动，点击查看详情！",
    },
  ],
];

mock("/user/getMessages", "get", () => {
  const i = Math.floor(Math.random() * messageData.length - 0.01);
  return {
    code: 0,
    message: "获取成功",
    data: messageData[i],
  };
});

mock("/user/sendMessage", "post", () => {
  return {
    code: 0,
    message: "发送成功",
  };
});
