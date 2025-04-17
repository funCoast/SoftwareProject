import json
from datetime import datetime

from django.http import JsonResponse
from rest_framework.decorators import api_view

from backend.models import Agent, Comment, User


@api_view(['POST'])
def agent_send_comment(request):
    try:
        data = json.loads(request.body)

        agent_id = data['agent']
        user_id = data['uid']
        comment = data['comment']

        if not agent_id:
            return JsonResponse({
                'code': -1,
                'message': '缺少参数 agent',
            })

        if not user_id:
            return JsonResponse({
                'code': -1,
                'message': '用户为空'
            })

        if not comment:
            return JsonResponse({
                'code': -1,
                'message': '不能发送空评论'
            })

        try:
            agent = Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'message': '该智能体不存在'
            })

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'message': '用户不存在'
            })

        comment = Comment.objects.create(
            agent=agent,
            user=user,
            content=comment,
            comment_time=datetime.now(),
        )

        return JsonResponse({
            'code': 0,
            'message': '评论添加成功'
        })
    except Exception as e:
        return JsonResponse({
            'code': -1,
            'message': str(e)
        })


@api_view(['GET'])
def agent_get_comments(request):
    if request.method == 'GET':
        try:
            agent_id = request.GET.get('agent')
            if not agent_id:
                return JsonResponse({
                    'code': -1,
                    'message': '缺少参数 agent',
                    'data': []
                })

            # 获取智能体
            try:
                agent = Agent.objects.get(agent_id=agent_id)
            except Agent.DoesNotExist:
                return JsonResponse({
                    'code': -1,
                    'message': '智能体不存在',
                    'data': []
                })

            # 获取该智能体的所有评论
            comments = Comment.objects.filter(agent=agent).select_related('user').order_by('comment_time')

            # 构建响应数据
            data = []
            for idx, comment in enumerate(comments, start=1):
                user = comment.user
                data.append({
                    'id': idx,
                    'name': user.username,
                    'userId': user.user_id,
                    'avatar': user.avatar.url if user.avatar else "",
                    'content': comment.content,
                    'time': comment.comment_time.isoformat()
                })

            return JsonResponse({
                'code': 0,
                'message': '获取成功',
                'data': data
            })

        except Exception as e:
            return JsonResponse({
                'code': -1,
                'message': f'服务器错误: {str(e)}',
                'data': []
            })
    else:
        return JsonResponse({
            'code': -1,
            'message': '仅支持 GET 请求',
            'data': []
        })