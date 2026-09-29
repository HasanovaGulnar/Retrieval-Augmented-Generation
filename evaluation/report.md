# Retrieval-Augmented Generation: evaluation

Retrieval Hit-rate@3: 100%

## Actual model outputs

| Question | With retrieval | LLM alone |
|---|---|---|
| Apellyasiya Qaydaları adlı 5-ci bölmədə müraciət müddəti nədir? | Apellyasiya Qaydaları - Nəticədən narazı olan tələbə, nəticələrin elan edildiyi gündən 24 saat ərzində Apellyasiya Komissiyasina ərizəsi ilə müraciət etməlidir. [imtahan_qaydalari_p021_c001] | Müraciət müddəti 30 gündən az olmasa, 30 gündən az olmasa 30 gündən artıq olmalıdır. |
| 4.7-ci bölmədə tələbənin apellyasiya üçün müraciət müddəti nədir? | İmtahan nəticələrinin qiymətləndirilməsindən və ya sualların (testl ərin) tərtibatından narazılığı olduğu halda, 3 iş günü ərzində Apellyasiya komissiyasına müraciət etmək. [imtahan_qaydalari_p018_c002] | Müraciət müddəti 10 gündən az olmasa, 10 gündən az olmasa 30 gündən az olmasa 3 aydan az olmasa 3 aydan az olmasa 6 aydan az olmasa 1 ilə qədər dəyərdir. |
| İmtahan zalına hansı əşyaları gətirmək qadağandır? | İmtahan zalına cib telefonu, kalkulyator, konspekt, qeydiyyat kitabçası, çanta və s. texniki vasitələri gətirmək; [imtahan_qaydalari_p019_c001] | İmtahan zalına əlavə olaraq ədviyyat, qədəm, qəbul edə biləcək əşyalar gətirmək qadağandır. |
| İmtahan qaydalarını pozaraq zaldan xaric edilən tələbəyə neçə bal verilir? | imtahandan xaric edilir və imtahanın nəticəsinə görə ona “0” (sıfır) bal müəyyənləşdirilir. 2. [imtahan_qaydalari_p019_c002] | Məlumdur ki, imtahan qaydalarını pozaraq zaldan xaric edilən tələbəyə 0 bal verilir. |
| 4.8-ci bölmədə i̇mtahan başlayandan neçə dəqiqə sonra gecikmiş tələbə zala buraxılmır? | - İmtahanın başlanma vaxtından etibar ən 15 d əqiqə ərzində heç bir t əhsilalanın zalı t ərk etməsinə imkan verməmək v ə imtahan başladıqdan 15 d əqiqə sonra imtahana g ələn təhsilalanların imtahan zalına daxil olmasına icazə verməmək; [imtahan_qaydalari_p020_c002] | Məlumatəsdiyyatə əsasən, 4.8-ci bölmədə i̇mtahan başlayandan 3 dəqiqədən artıq gecikmədən sonra tələbə zala buraxılmır. |

## Out-of-scope checks

- Universitet yeməkxanasında bu gün hansı yeməklər verilir?: declined=True
- Mars planetinin neçə təbii peyki var?: declined=True

## Same-prompt retrieval-disabled test

Changed answers: 5/5.
Same LLM and system prompt; no FAISS or document loading in disabled mode.
The LLM receives empty CONTEXT. Raw selections are saved.

## Separate generation review

- Q1: {"answer_correct": true, "rag_supported_by_sources": true, "citations_correct": true, "meaningful_difference": true, "notes": "Correct 24-hour deadline from section 5; baseline invents a different deadline."}
- Q2: {"answer_correct": true, "rag_supported_by_sources": true, "citations_correct": true, "meaningful_difference": true, "notes": "Correct 3-working-day deadline from section 4.7; baseline invents multiple timeframes."}
- Q3: {"answer_correct": true, "rag_supported_by_sources": true, "citations_correct": true, "meaningful_difference": true, "notes": "Correct prohibited-item list, quoted from the relevant prohibition list; baseline is incoherent."}
- Q4: {"answer_correct": true, "rag_supported_by_sources": true, "citations_correct": true, "meaningful_difference": false, "notes": "Correct zero-point rule. Baseline also states zero: factual agreement is recorded, not hidden. Retrieval-disabled run still refuses."}
- Q5: {"answer_correct": true, "rag_supported_by_sources": true, "citations_correct": true, "meaningful_difference": true, "notes": "Correct 15-minute exclusion rule specifically from section 4.8; does not resolve the separate section 4.3 provision."}

These are development-set results, not held-out accuracy.
The late-arrival question explicitly names section 4.8 because section 4.3
contains a different late-arrival provision. Historical results are retained.