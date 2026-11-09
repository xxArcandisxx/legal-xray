# Legal X-ray test files

| File | What it tests |
|---|---|
| english_rental_agreement.txt / .pdf | English text upload, and a normal text-based PDF |
| english_job_offer.txt | English job offer |
| english_legal_notice.txt | English legal notice |
| hindi_rental_agreement.txt | Hindi document, English/Hindi/Kannada toggle |
| hindi_job_offer.txt | Hindi job offer |
| kannada_rental_agreement.txt | Kannada document |
| kannada_job_offer.txt | Kannada job offer |
| ocr_test_hindi_rental_photo.png | OCR on a photo of a Hindi page |
| ocr_test_kannada_job_offer_photo.png | OCR on a photo of a Kannada page |
| ocr_test_english_legal_notice_scan.pdf | OCR on a scanned (image-only) PDF |

The OCR files need your API key. The .txt and text-based .pdf files go through the normal path.

## Risky clauses planted (the AI should flag most of these)
- **Rental:** deduction from deposit with no receipts, 18-month lock-in with full rent payable, 15% rent hike every 6 months, no overnight guests, landlord can terminate anytime, Rs 2,000 painting charge even with no damage.
- **Job offer:** 30% variable pay at company's discretion, no salary for 2 months of probation, 3-year bond with Rs 2,00,000 penalty, 90-day vs 7-day notice, 2-year non-compete, 12-hour days without extra pay, ownership of personal-time inventions.
- **Legal notice:** 36% interest plus penalties, 7-day deadline, vehicle seizure threat, legal fees charged to you, waiver of the right to dispute.

## What to check
1. Highlights land on the right sentences (this proves the quote matching works).
2. The language buttons change all explanations and tips.
3. Hindi and Kannada documents load and get highlighted.
4. OCR files show the transcribed text on the left, then highlights.
