"""Small synthetic regression tests; no website data or practice answers embedded."""
import unittest
from types import SimpleNamespace
try:
    from submission.solution import build
except ImportError:
    from solution import build


def page(url,title,text):
    return SimpleNamespace(url=url,title=title,markdown=text,fetched_at='2026-01-01')


def snapshot(date,pages):
    return SimpleNamespace(snapshot_id=date,taken_on=date,pages=pages)


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.k=build()
        old=page('https://example-cu.test/rates/certificates','Certificates',
                 '# Certificates\n\n6-month certificate APY: 2.95%\n\n12-month certificate APY: 3.10%')
        self.k.ingest(snapshot('2026-01-05',[old]))
        new=page('https://example-cu.test/rates/certificates','Certificates',
                 '# Certificates\n\n6-month certificate APY: 3.50%\n\n12-month certificate APY: 3.10%')
        fees=page('https://example-cu.test/fees','Fees',
                  '# Fees\n\nLost debit card replacement: $2.50')
        self.k.ingest(snapshot('2026-03-01',[new,fees]))

    def test_current_value_and_source(self):
        ans=self.k.answer('What is the 6-month certificate APY?')
        self.assertIn('3.50%',ans.text)
        self.assertNotIn('2.95%',ans.text)
        self.assertEqual(ans.sources[0].url,'https://example-cu.test/rates/certificates')

    def test_as_of(self):
        ans=self.k.answer('What was the 6-month certificate APY?',as_of='2026-01-31')
        self.assertIn('2.95%',ans.text)
        self.assertNotIn('3.50%',ans.text)

    def test_repeat_and_paraphrase(self):
        a=self.k.answer('What is the 6-month certificate APY?').text
        self.assertEqual(a,self.k.answer('What is the 6-month certificate APY?').text)
        self.assertIn('3.50%',self.k.answer('Current APY on a six month share certificate?').text)

    def test_refuses_unavailable_tier(self):
        ans=self.k.answer('What is the 60-month jumbo certificate rate?')
        self.assertFalse(ans.confident)
        self.assertNotIn('3.50%',ans.text)

    def test_fee(self):
        self.assertIn('$2.50',self.k.answer('How much is lost debit card replacement?').text)

    def test_detects_numeric_change(self):
        conflicts=self.k.conflicts()
        self.assertTrue(any('2.95%' in c.values and '3.50%' in c.values
                            and c.resolution=='3.50%' for c in conflicts))

    def test_exact_qualifiers(self):
        system=build()
        auto=page('https://example-cu.test/personal/loans/auto-motorcycle-loans',
                  'Auto Loans', '# Auto Loans\n\n## Auto Loan Rates\n\n'
                  '| Loan Program | Term | Annual Percentage Rate (As Low As) |\n'
                  '| --- | --- | --- |\n'
                  '| 2024-27 Model Year | 48 Months | 5.19% APR |\n'
                  '| 2024-27 Model Year | 60 Months | 5.39% APR |\n'
                  '| 2024-27 Model Year | 84 Months | 5.59% APR |\n'
                  '| 2021-23 Model Year | 60 Months | 5.64% APR |')
        system.ingest(snapshot('2026-09-28',[auto]))
        a=system.answer('APR for a 60-month auto loan for a 2025 model-year vehicle?')
        self.assertIn('5.39%',a.text)
        self.assertNotIn('5.64%',a.text)
        b=system.answer('APR for an 84-month auto loan for a 2024 model-year vehicle?')
        self.assertIn('5.59%',b.text)

    def test_personal_card_not_business_card(self):
        system=build()
        system.ingest(snapshot('2026-09-28',[
            page('https://example-cu.test/personal/credit-cards','Credit Cards',
                 '# Credit Cards\n### Platinum Visa\n- Standard ongoing rate: 12.50%-19.50% APR\n- Intro 2.90% balance transfer APR.'),
            page('https://example-cu.test/business/credit-cards','Business Cards',
                 '# Business Credit Cards\n### Business Platinum Visa\n- Variable 15.50% APR')]))
        a=system.answer('What is the standard purchase APR on the Platinum Visa?')
        self.assertIn('12.50%',a.text)
        self.assertNotIn('15.50%',a.text)


    def test_authoritative_auto_rate_beats_stale_promotion(self):
        system=build()
        official=page('https://example-cu.test/personal/loans/auto-loans/', 'Auto Loan Rates',
            '# Auto Loan Rates\n\n| Loan Program | Term | Annual Percentage Rate (As Low As) |\n'
            '| --- | --- | --- |\n| 2024-27 Model Year | 60 Months | 5.39% APR |\n'
            '| 2024-27 Model Year | 84 Months | 5.59% APR |')
        stale=page('https://example-cu.test/switch-and-earn','Switch and Earn',
            '# Special offers\n\n| Loan Program | Term | Annual Percentage Rate (As Low As) |\n'
            '| --- | --- | --- |\n| 2023–26 Model Year | 60 Months | 5.34% APR |\n'
            '| 2023–26 Model Year | 84 Months | 5.54% APR |')
        system.ingest(snapshot('2026-09-28',[stale,official]))
        a=system.answer('APR on a 60 month auto loan for a 2025 vehicle')
        self.assertIn('5.39%',a.text)
        self.assertNotIn('5.34%',a.text)
        self.assertIn('/personal/loans/auto-loans/',a.sources[0].url)
        c=system.conflicts()
        self.assertTrue(any('5.39%' in x.values and '5.34%' in x.values and x.resolution=='5.39%' for x in c))

    def test_last_approved_fee_carried_forward_when_page_omitted(self):
        system=build()
        old=page('https://example-cu.test/fees','Fees',
            '# Fees\n\nLost debit card replacement fee: $2.50')
        news=page('https://example-cu.test/news','News','# News\n\nCredit union news')
        system.ingest(snapshot('2026-01-05',[old]))
        system.ingest(snapshot('2026-03-01',[news]))
        ans=system.answer('How much is the lost debit card replacement fee?')
        self.assertIn('$2.50',ans.text)
        self.assertEqual('2026-01-05',ans.sources[0].snapshot_id)

    def test_refusal_before_first_snapshot(self):
        ans=self.k.answer('What is the 6-month certificate APY?',as_of='2025-10-01')
        self.assertFalse(ans.confident)
        self.assertEqual([],ans.sources)


if __name__=='__main__':
    unittest.main()