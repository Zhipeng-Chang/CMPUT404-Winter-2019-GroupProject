from django.test import Client, TestCase
from django.urls import reverse
import uuid
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User
import datetime



class TestViews(TestCase):
    def setUp(self):
        # https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
        # create first user author client
        self.user = User.objects.create(username='testuser1')
        self.user.set_password('test')
        self.user.save()
        self.client = Client()
        self.client.login(username='testuser1', password='test')
        self.author = Author.objects.create(user=self.user, displayName='author1',
                                            github='https://github.com/terrence85561')

        # create another user author client
        self.other_user = User.objects.create(username='testuser2')
        self.other_user.set_password('test')
        self.other_user.save()
        self.other_client = Client()
        self.other_client.login(username='testuser2',password='test')
        self.other_author = Author.objects.create(user=self.other_user,displayName='author2',
                                                  github='https://github.com/terrence85561')

        self.new_post_url = reverse('new_post')

    def test_New_Post_Handler_POST_API(self):

        response = self.client.post(self.new_post_url,{
            'title': 'POST1',
            'description': 'post for testing',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
            'content': 'test'
        })
        self.assertEquals(response.status_code, 200)

    def test_Post_Handler_GET_OTHER_AUTHOR_POST_API(self):
        # test of post_handler class
        # test get other author's post
        self.other_client.post(self.new_post_url,{
                'title': 'original post1',
                'content': 'This is a test post',
                'categories': 'test',
                'contentType': 'text/plain',
                'author': self.other_author,
                'visibility': 'PUBLIC',
                'description': 'test description'

        })

        post1 = Post.objects.get(title='original post1')
        post1_postid = post1.postid
        modify_post_url = reverse('modify_post',args=[post1_postid])

        response = self.client.get(modify_post_url)

        self.assertEquals(response.status_code,200)

    def test_Post_Handler_GET_MY_POST_API(self):
        # test visit my post and it is private to me
        self.client.post(self.new_post_url,{
            'title': 'my post',
            'content': 'This is my post',
            'categories': 'test',
            'contentType': 'text/plain',
            'author': self.author,
            'visibility': 'PRIVATE',
            'description': 'test description'
        })

        post1 = Post.objects.get(title='my post')
        post1_postid = post1.postid
        modify_post_url = reverse('modify_post',args=[post1_postid])
        response = self.client.get(modify_post_url)
        self.assertEquals(response.status_code,200)

        # test other user cannot visit my post
        other_response = self.other_client.get(modify_post_url)
        self.assertEquals(other_response.status_code,404)
        #print(other_response.content.decode('utf-8'))

    def test_Post_Handler_PUT_API(self):
        # first create a public post, test other user can see it or not
        # then modified to private and change title, test title, test status code,
        # test other user can see it or not

        # create a post
        self.client.post(self.new_post_url,{
            'title': 'original post2',
            'content': 'This is a test post',
            'categories': 'test',
            'contentType': 'text/plain',
            'author': self.author,
            'visibility': 'PUBLIC',
            'description': 'test description'
        })
        obj = Post.objects.get(title='original post2')
        post1_postid = obj.postid
        modify_post_url = reverse('modify_post',args=[post1_postid])
        response_get=self.other_client.get(modify_post_url)
        self.assertEquals(response_get.status_code,200)

        response = self.client.put(modify_post_url,json.dumps({
            'title':'modified my title',
            'visibility':'PRIVATE',
            'description':'test description',
            'contentType' : 'text/plain',
            'content': 'This is a test post'
        }),content_type='application/json')
        self.assertEquals(response.status_code,200)
        # emmmm...
        post = Post.objects.get(pk=post1_postid)
        self.assertEquals(post.title,'modified my title')
        response_get=self.other_client.get(modify_post_url)
        self.assertEquals(response_get.status_code,404)

    def test_Post_Handler_DELETE_API(self):
        # create a post first, test status code == 204
        # test if the post still exist, test if other user can delete it

        # create a public post
        self.client.post(self.new_post_url,{
            'title': 'need delete',
            'content': 'This is my post',
            'categories': 'test',
            'contentType': 'text/plain',
            'author': self.author,
            'visibility': 'PUBLIC',
            'description': 'test description'
        })
        post = Post.objects.get(title='need delete')
        post_id = post.postid
        modify_post_url = reverse('modify_post',args=[post_id])

        # test if other user can delete it or not
        response = self.other_client.delete(modify_post_url)
        self.assertEquals(response.status_code,404)

        # test if current user can delete it or not
        response1 = self.client.delete(modify_post_url)
        self.assertEquals(response1.status_code,204)

        # test if the post still exist or not
        self.assertFalse(Post.objects.filter(pk=post_id).exists())

    def test_Comment_Handler_POST_API(self):
        # create a public post first , then test if user can add comment on it
        # then create a private post, then test if user can add comment on it.

        # create a public post
        self.other_client.post(self.new_post_url,{
            'title': 'comment this post!',
            'content': 'please make some comments',
            'categories': 'test',
            'contentType': 'text/plain',
            'author': self.other_author,
            'visibility': 'PUBLIC',
            'description': 'test description'
        })
        post = Post.objects.get(title='comment this post!')
        post_id = post.postid

        # create a comment on this post
        # get the reverse url
        comment_url = reverse('comment',args=[post_id])
        response=self.client.post(comment_url,{
            'query': 'addComment',
            'post': 'testserver',
            'comment': {
                'author': {
                    'id': self.author.id,
                    'host': 'xxx',
                    'displayName': self.author.displayName,
                    'url': 'xxx',
                    'github': self.author.github
                },
                'comment': 'this is my first comment',
                'contentType': 'text/plain',
                'published': datetime.datetime.now(),
            }
        })
        self.assertEquals(response.status_code,200)

        # create a private post
        self.other_client(self.new_post_url,{
            'title': 'comment this private post',
            'content': 'please make some comments',
            'categories': 'test',
            'contentType': 'text/plain',
            'author': self.other_author,
            'visibility': 'PRIVATE',
            'description': 'test description'
        })
        post1 = Post.objects.get(titile='comment this private post')
        post1_id = post1.postid

        comment_url_private = reverse('comment',args=[post1_id])
        response1=self.client.post(comment_url_private,{
            'query': 'addComment',
            'post': 'testserver',
            'comment': {
                'author': {
                    'id': self.author.id,
                    'host': 'xxx',
                    'displayName': self.author.displayName,
                    'url': 'xxx',
                    'github': self.author.github
                },
                'comment': 'this is comment from author1',
                'contentType': 'text/plain',
                'published': datetime.datetime.now(),
            }
        })
        self.assertEquals(response1.status_code,403)

        response2 = self.client.post(comment_url_private, {
            'query': 'addComment',
            'post': 'testserver',
            'comment': {
                'author': {
                    'id': self.other_author.id,
                    'host': 'xxx',
                    'displayName': self.other_author.displayName,
                    'url': 'xxx',
                    'github': self.other_author.github
                },
                'comment': 'this is comment from author2',
                'contentType': 'text/plain',
                'published': datetime.datetime.now(),
            }
        })
        self.assertEquals(response2.status_code,200)