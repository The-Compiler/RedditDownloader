import praw.models
from static import stringutil
import re


class RedditElement(object):
	"""
		A wrapper class to store & process Reddit Post/Comment data.
		Attributes:
			type: A String of this element's original type, either "Post" or "Comment".
			id: A string representing the (Post 'name' or Comment 'link_id') of this element.
			subreddit: A string representing the subreddit name owning this element.
			title: A string representing the title of the Post belonging to this element.
			author: string representing the author of this element.
			_urls: A String Array of urls parsed for this post/comment.
			body: The body of text iin this Post.
			parent: The ID of this Post's parent Submission, if this Element is a Comment. Otherwise NULL.
	"""

	def __init__(self, obj):
		""" Creates the object. Automatically calls its own detect_type() function to resolve variable name mappings. """
		self._urls = []
		self.type = None
		self.id = None
		self.title = None
		self.author = None
		self.body = None
		self.parent = None
		self.subreddit = None
		self.detect_type(obj)

		self.over_18 = obj.over_18
		self.created_utc = obj.created_utc
		self.num_comments = obj.num_comments
		self.score = obj.score
		self.link_count = len(self._urls)
		self.source_alias = None

		assert self.type == 'Submission' or self.type == 'Comment'
		assert self.id is not None

	def detect_type(self, obj):
		""" Simple function to call the proper Comment or Submission handler. """
		# noinspection PyUnresolvedReferences
		tp = type(obj)
		stp = str(tp).lower()
		if type(obj) == praw.models.Submission:
			self._submission(obj)
		elif type(obj) == praw.models.reddit.comment.Comment:
			self._comment(obj)
		elif 'submission' in stp:
			self._ps_submission(obj)
		elif 'comment' in stp:
			self._ps_comment(obj)
		else:
			raise Exception('Unknown Element Type: '+str(type(obj)))
	
	def _comment(self, c):
		""" Handle a Comment object. """
		# out("[Comment](%s): %s" % (c.subreddit.display_name, c.link_title) )
		self.type = 'Comment'
		self.id = str(c.name)
		self.parent = str(c.link_id)
		self.title = str(c.link_title)
		self.subreddit = str(c.subreddit.display_name)
		if c.author:
			self.author = str(c.author.name)
		else:
			self.author = 'Deleted'
		self.body = c.body
		for url in stringutil.html_elements(c.body_html, 'a', 'href'):
			self.add_url(url)

	def _ps_comment(self, c):
		raise Exception("PushShift Comments cannot be wrapped - They are lacking crucial details!")

	def _submission(self, post):
		""" Handle a Submission. """
		# out("[Post](%s): %s" % (post.subreddit.display_name, post.title) )
		self.type = 'Submission'
		self.id = str(post.name)
		self.title = str(post.title)
		self.subreddit = str(post.subreddit.display_name)
		if post.author is None:
			self.author = 'Deleted'
		else:
			self.author = str(post.author.name)
		self.body = post.selftext
		if post.selftext.strip() != '':
			# This post probably doesn't have a URL, and has selftext instead.
			for url in stringutil.html_elements(post.selftext_html, 'a', 'href'):
				self.add_url(url)
		if post.url is not None and post.url.strip() != '':
			self.add_url(post.url)

	def _ps_submission(self, post):
		self.type = 'Submission'
		self.id = post.id
		if 't3_' not in self.id:
			self.id = 't3_%s' % self.id
		self.title = post.title
		self.subreddit = post.subreddit
		if post.author is None or post.author == '[deleted]':
			self.author = 'Deleted'
		else:
			self.author = str(post.author)
		self.body = post.selftext if 'selftext' in post and post.selftext else ''
		if post.url is not None and post.url.strip() != '' and 'reddit.com' not in post.url:
			self.add_url(post.url)
		if self.body.strip():
			for u in re.findall(r'\[.+?\]\s*?\((.+?)\)', self.body):
				self.add_url(u)

	def add_url(self, url):
		""" Add a URL to this element. """
		if any(url.strip().startswith(x) for x in ['/u/', '/r/']):
			return
		if url not in self._urls:
			self._urls.append(url)

	def remove_url(self, url):
		if url in self._urls:
			self._urls.remove(url)
		else:
			print("Cannot remove:", url)

	def set_source(self, source_obj):
		"""  Sets this Element's source alias by pulling it directly from the object.  """
		self.source_alias = str(source_obj.get_alias())

	def get_id(self):
		""" Get this element's ID. """
		return self.id

	def get_urls(self):
		""" Returns a list of all this element's UNIQUE urls. """
		return self._urls[:]
