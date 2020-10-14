import static.praw_wrapper as pw
import static.settings as settings
import praw.models
from processing.wrappers.redditelement import RedditElement
from tests.mock import EnvironmentTest


class PrawWrapperTest(EnvironmentTest):
	env = 'rmd_version_4'

	def setUp(self):
		settings.load(self.settings_file)

	def test_load_comment(self):
		""" Load Comment directly by ID """
		com = pw.get_comment(t1_id='t1_dxz6n80')
		re = RedditElement(com)
		vals = {
			"_urls": ['https://stackoverflow.com/a/23709194'],
			"type": 'Comment',
			"id": 't1_dxz6n80',
			"title": 'Reddit Media Downloader is now Threaded - Scrape all the subreddits, *much* faster now.',
			"author": 'theshadowmoose',
			"parent": 't3_8ewkx2',
			"subreddit": 'DataHoarder',
			"over_18": False,
			"created_utc": 1524705293.0,
			"link_count": 1,
			"source_alias": None,
		}
		for k, v in vals.items():
			self.assertEqual(getattr(re, k), v, msg='%s was not properly set in Comment!' % k.title())

	def test_load_submission(self):
		""" Load submission directly by ID """
		p = pw.get_submission(t3_id='t3_6es0u8')
		re = RedditElement(p)
		self.assertEqual(re.author, 'theshadowmoose', msg='Submission has invalid Author!')
		self.assertEqual(re.title, 'Test Direct Link', msg='Submission has invalid Title!')

	def test_submission_gallery(self):
		""" Parse all gallery links """
		p = pw.get_submission(t3_id='t3_hrrh23')
		re = RedditElement(p)
		self.assertEqual(len(re.get_urls()), 3, msg='Got incorrect image count from reddit gallery submission!')
		for url in re.get_urls():
			self.assertIn('https', url, msg='Failed to extract valid gallery URL: %s' % url)

	def test_frontpage_load(self):
		""" Load frontpage Submissions """
		posts = [p for p in pw.frontpage_posts(limit=3)]
		self.assertEqual(len(posts), 3, msg="PRAW found the wrong number of posts.")

	def test_liked_saved(self):
		""" Load Liked/Saved Posts """
		cnt = 0
		for p in pw.my_liked_saved():
			cnt += 1
			self.assertTrue(p, msg='Found invalid Post!')
		self.assertGreater(cnt, 0, msg="Found no Liked/Saved Posts!")

	def test_subreddit_submissions(self):
		""" Load submissions from a subreddit """
		self.assertGreater(len([p for p in pw.subreddit_posts('shadow_test_sub', limit=5)]), 3, msg='Loaded too few Posts.')

	def test_user_posts(self):
		""" Load test user posts """
		posts = [p for p in pw.user_posts('test_reddit_scraper', find_comments=True, find_submissions=True)]
		for p in posts:
			self.assertEqual(p.author, 'test_reddit_scraper', msg='Invalid Post author!')

	def test_get_submission_comments(self):
		""" Findina a Submission's comments should work """
		posts = list(pw.get_submission_comments('t3_79pp8r'))
		self.assertGreater(len(posts), 0, msg="Failed to load child comments from Submission!")

	def test_get_current_username(self):
		""" Getting the signed-in user should work """
		self.assertTrue(pw.get_current_username(), msg="Failed to load the active username!")

	def test_get_info(self):
		""" Getting generic ID info should work """
		posts = list(pw.get_info(['t1_c6k3thm', 't3_79pp8r']))
		self.assertEqual(len(posts), 2, msg='Failed to find correct amount of generic Info!')
		self.assertIsInstance(posts[0], praw.models.Comment, msg="Didn't find a Comment!")
		self.assertIsInstance(posts[1], praw.models.Submission, msg="Didn't find a Submission!")

	def test_post_orders(self):
		""" All post orders should find a result from a subreddit """
		for order, time in pw.post_orders()+[('best', False)]:
			post = next(pw.subreddit_posts('funny', order, 1, 'all'))
			self.assertTrue(post, msg="Failed to find '%s' post." % order)
