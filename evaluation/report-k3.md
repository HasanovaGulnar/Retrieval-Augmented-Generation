# Document RAG — qiymətləndirmə

Retrieval Hit-rate@3: 10/10 = 100%

## Retrieval ilə və retrieval olmadan

| Sual | RAG cavabı | Sənədsiz cavab |
|---|---|---|
| Apellyasiya Qaydaları adlı 5-ci bölmədə müraciət müddəti nədir? | Apellyasiya müraciət etməyən tələbənin imtahan işinə baxılmağa icazə verilir.<br><br>Mənbələr: [imtahan_qaydalari_p021_c001] | Apellyasiya qaydaları adlı bölmədə 5-ci müraciət müddəti ən az 24 saat olaraq təqdim olunmalıdır. |
| 4.7-ci bölmədə tələbənin apellyasiya üçün müraciət müddəti nədir? | Tələbən 24 saat ərzində apellyasiya komissiyasına müraciət etməlidir.<br><br>Mənbələr: [imtahan_qaydalari_p021_c001] | 4.7-ci bölmədə tələbənin apellyasiya üçün müraciət müddəti 15 gün olur. |
| İmtahan zalına hansı əşyaları gətirmək qadağandır? | İmtahan zalına telefon, kalkulyator, konspekt, qeydiyyat kitabçası, çanta və s. texniki vasitələri gətirmək qadağandır.<br><br>Mənbələr: [imtahan_qaydalari_p019_c001], [imtahan_qaydalari_p016_c002], [imtahan_qaydalari_p020_c002] | İmtahan zalına qadagandır əşyalaları gətirmək, amma konkret məlumat yoxdur. Zalının təşkilatı və istifadəsi ilə bağlı olaraq gətirilmək məşq edən əşyalalar olacaq. |
| İmtahan qaydalarını pozaraq zaldan xaric edilən tələbəyə neçə bal verilir? | İmtahan qaydalarına görə, tələbə imtahandan xaric edilir və imtahanın nəticəsinə görə ona '0' (sıfır) bal müəyyənləşdirilir.<br><br>Mənbələr: [imtahan_qaydalari_p019_c001], [imtahan_qaydalari_p019_c002] | İmtahan qaydaları ilə bağlı məlumat yoxdur və buna uyğun olaraq, sənət qaydaları haqqında məlumat yoxdur. |
| İmtahan başlayandan neçə dəqiqə sonra gecikmiş tələbə zala buraxılmır? | İmtahan başlayandan 15 dəqiqə sonra gecikmiş tələbə zala buraxılmır.<br><br>Mənbələr: [imtahan_qaydalari_p014_c002], [imtahan_qaydalari_p020_c002] | Gecikmiş tələbə zala gecikmədən 15 dəqiqə sonra buraxılır. |

## Sənəddənkənar suallar

- Universitet yeməkxanasında bu gün hansı yeməklər verilir? — imtina: BƏLİ
- Mars planetinin neçə təbii peyki var? — imtina: BƏLİ

## Generation qiymətləndirməsi

grounding_results.json daxilində review sahələri əl ilə doldurulmalıdır.
Faktların mənbə ilə uyğunluğu, istinadların düzgünlüyü və cavabların
məzmun baxımından fərqlənməsi ayrıca yoxlanmalıdır.
Sadəcə sözlərin fərqli olması grounding sübutu deyil.