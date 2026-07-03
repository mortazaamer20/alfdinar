from django.test import TestCase
from django.urls import reverse

from .models import Case, CaseImage, Visit, VisitImage


class VideoEmbedTests(TestCase):
    """The video_embed_url property normalises YouTube links for <iframe>s."""

    def test_youtube_watch_url_is_converted(self):
        v = Visit(video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.assertEqual(v.video_embed_url,
                         'https://www.youtube.com/embed/dQw4w9WgXcQ')

    def test_youtu_be_short_url_is_converted(self):
        c = Case(video_url='https://youtu.be/dQw4w9WgXcQ')
        self.assertEqual(c.video_embed_url,
                         'https://www.youtube.com/embed/dQw4w9WgXcQ')

    def test_shorts_url_is_converted(self):
        v = Visit(video_url='https://www.youtube.com/shorts/dQw4w9WgXcQ')
        self.assertEqual(v.video_embed_url,
                         'https://www.youtube.com/embed/dQw4w9WgXcQ')

    def test_blank_url_returns_empty(self):
        self.assertEqual(Visit(video_url='').video_embed_url, '')

    def test_non_youtube_url_is_unchanged(self):
        url = 'https://example.com/video.mp4'
        self.assertEqual(Case(video_url=url).video_embed_url, url)


class DetailViewTests(TestCase):
    def test_visit_detail_page_loads(self):
        visit = Visit.objects.create(title='زيارة عائلة الشهيد')
        VisitImage.objects.create(visit=visit, image='visits/x.jpg')
        resp = self.client.get(reverse('core:visit_detail', args=[visit.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'زيارة عائلة الشهيد')

    def test_case_detail_page_loads(self):
        case = Case.objects.create(title='حالة علاج')
        CaseImage.objects.create(case=case, image='cases/x.jpg')
        resp = self.client.get(reverse('core:case_detail', args=[case.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'حالة علاج')

    def test_missing_visit_returns_404(self):
        resp = self.client.get(reverse('core:visit_detail', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_visits_list_links_to_detail(self):
        visit = Visit.objects.create(title='زيارة ميدانية')
        resp = self.client.get(reverse('core:visits'))
        self.assertContains(resp, reverse('core:visit_detail', args=[visit.pk]))

    def test_cases_list_links_to_detail(self):
        case = Case.objects.create(title='حالة')
        resp = self.client.get(reverse('core:cases'))
        self.assertContains(resp, reverse('core:case_detail', args=[case.pk]))
