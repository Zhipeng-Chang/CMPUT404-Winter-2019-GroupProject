from django.test import Client, TestCase
from django.urls import reverse
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User
from django.test import LiveServerTestCase

class TestFriendQueryHandler(LiveServerTestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='testuser1')
        self.user1.set_password('test')
        self.user1.save()
        self.client1=Client()
        self.client1.login(username='testuser1',password='test')
        self.author1 = Author.objects.create(user=self.user1,displayName='author1',
                                             host=self.live_server_url+'/',
                                             github='https://github.com/terrence85561')
        self.user2 = User.objects.create(username='testuser2')
        self.user2.set_password('test')
        self.user2.save()
        self.client2 = Client()
        self.client2.login(username='testuser2', password='test')
        self.author2 = Author.objects.create(user=self.user2, displayName='author2',
                                            host=self.live_server_url+'/',
                                            github='https://github.com/terrence85561')
        self.user3 = User.objects.create(username='testuser3')
        self.user3.set_password('test')
        self.user3.save()
        self.client3 = Client()
        self.client3.login(username='testuser3', password='test')
        self.author3 = Author.objects.create(user=self.user3, displayName='author3',
                                             host=self.live_server_url+'/',
                                             github='https://github.com/terrence85561')

    def test_get_friend_list(self):
        url = reverse('friendrequest')
        response=self.client1.post(url, {
            "query": "friendrequest",
            "author": {
                "id": self.author1.id,
                "host": self.author1.host,
                "displayName": self.author1.displayName,
                "url": self.author1.host + str(self.author1.id)
            },
            "friend": {
                "id": self.author2.id,
                "host": self.author2.host,
                "displayName": self.author2.displayName,
                "url": self.author2.host + str(self.author2.id)
            }
        }, 'application/json')
        friend_request_id1 = Friend.objects.filter(author=self.author1,friend=self.author2)[0].id
        self.client2.put(url, {
            "id": friend_request_id1,
            "status": "Accept"
        }, 'application/json')

        self.client1.post(url, {
            "query": "friendrequest",
            "author": {
                "id": self.author1.id,
                "host": self.author1.host,
                "displayName": self.author1.displayName,
                "url": self.author1.host + '/' + str(self.author1.id)
            },
            "friend": {
                "id": self.author3.id,
                "host": self.author3.host,
                "displayName": self.author3.displayName,
                "url": self.author3.host + '/' + str(self.author3.id)
            }
        }, 'application/json')

        friend_request_id2 = Friend.objects.filter(author=self.author1,friend=self.author3)[0].id

        self.client3.put(url,{
            "id":friend_request_id2,
            "status":"Accept"
        },'application/json')

        query_url = reverse('friendquery',args=[self.author1.id])
        response = self.client1.get(query_url)
        self.assertEquals(response.status_code,200)
        friendlist_length = len(json.loads(response.content)['authors'])
        self.assertEquals(friendlist_length,2)

    def test_post_friend_query(self):
        Friend.objects.create(author=self.author1,friend=self.author2,status="Accept")
        # check which authors in the list are friend of the author.
        url = reverse('friendquery',args=[self.author2.id])
        response=self.client1.post(url,{
            "query":"friends",
            "author":self.author1.host+'service/author/'+str(self.author1.id),
            "authors":[
                self.author2.host+'service/author/'+str(self.author2.id),
            ]
        },'application/json')

        self.assertEquals(response.status_code,200)
        
        data = json.loads(response.content)
        self.assertEquals(data['authors'],[self.author2.host+'service/author/'+str(self.author2.id)])