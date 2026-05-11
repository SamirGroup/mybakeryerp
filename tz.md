# Bunyod NON CRM - Texnik Vazifa (TZ) va Tizim Ishlash Jarayonlari

Ushbu hujjat "Bunyod NON" ishlab chiqarish va sotuvni avtomatlashtirish CRM tizimining joriy ishlash mantig'i, modullari va ma'lumotlar oqimini batafsil tushuntirib beradi.

---

## 1. HR (Xodimlar va Smenalar) Moduli
Tizimda ishlaydigan barcha xodimlar va ularning smenalari boshqariladi.
*   **Xodimlar (Employees):** Xodimlarning ism-sharifi, lavozimi (Sotuvchi, Novvoy va h.k.) va ishlash smenasi ro'yxatga olinadi.
*   **Kunlik hisobotlar (DailyReport):** Har bir xodim uchun ma'lum bir sana va smena bo'yicha kunlik hisobot ochiladi.
*   **Smena mantiqi:** Tizim asosan 2 ta smenada (masalan: 1-smena, 2-smena) ishlaydi. Sotuv yoki ishlab chiqarish amalga oshirilganda tizim avtomatik ravishda hozirgi faol smenani va unga biriktirilgan xodimni aniqlaydi.

---

## 2. Katalog va Ombor (Nomenklatura)
Barcha xom ashyo va tayyor mahsulotlar shu yerda boshqariladi.
*   **Xom ashyo (Raw Materials):** Ishlab chiqarishda ishlatiladigan un, yog', tuz kabi resurslar. Ularning nomi, o'lchov birligi (kg, gramm, litr, dona) va ombordagi fizik qoldig'i (stock) yuritiladi. Xom ashyo qoldig'i tugaganda tizim ogohlantiradi.
*   **Kategoriyalar va Mahsulotlar (Products):** Tayyor non mahsulotlari. Ularning rasmi, nomi, sotuv narxi va tayyor mahsulot omboridagi qoldig'i (Inventory) belgilanadi.
*   **Kunlik qoldiqlar (Day Balance):** Har bir tayyor mahsulot uchun kun boshidagi qoldiq (Opening balance) va kun oxiridagi qoldiq (Closing balance) yozib boriladi. Bu ertangi kunga qoldiqni o'tkazish (Carry-forward) uchun muhim.

---

## 3. Retseptlar (Texnologik xarita)
Ishlab chiqarishning asosi bo'lib, xom ashyoni avtomatik hisoblashga xizmat qiladi.
*   **1 dona mantiqi:** Har bir retsept **faqat 1 dona** tayyor mahsulot uchun yaratiladi.
*   **Tarkib (Ingredients):** Bitta nonni yopish uchun qaysi xom ashyodan qancha miqdorda (masalan, 0.350 kg yoki 350 gramm) ketishi belgilanadi.
*   **Tahrirlash:** Retseptni istalgan vaqt tahrirlash mumkin. Tahrirlanganda eski ingredientlar o'chirilib, yangilari yoziladi va saqlanadi.

---

## 4. Ishlab chiqarish (Production)
Jarayon to'liq nazorat ostida, xatoliklarni oldini olish tamoyili asosida ishlaydi.
*   **Jarayonni boshlash:** Foydalanuvchi mahsulotni tanlaydi va **necha dona** ishlab chiqarmoqchiligini (Miqdor) hamda taymer vaqtini kiritadi.
*   **Avtomatik xarajat:** Ishlab chiqarish boshlanishi bilan tizim kiritilgan donani retseptdagi 1 donalik miqdorga ko'paytirib, xom ashyo omboridan (RawMaterials) shu zahoti yechib oladi.
*   **Kutish bosqichi (Timer/Jarayon):** Ishlab chiqarilgan mahsulot darhol tayyor mahsulot omboriga tushmaydi. U "Jarayonda" qatoriga tushadi va belgilangan vaqt (timer) tugashini kutadi.
*   **Tasdiqlash:** Vaqt tugagach yoki nonlar tayyor bo'lgach, foydalanuvchi qo'lda **"Tayyor deb belgilash"** tugmasini bosishi va buni tasdiqlashi shart. Tasdiqdan so'nggina mahsulot rasman **Tayyor mahsulotlar omboriga (FinishedGoodsInventory)** qo'shiladi va sotuvga tayyor bo'ladi.

---

## 5. Sotuv (POS Dashboard)
Tayyor mahsulotlarni mijozlarga sotish va xodimlarning ulushini hisoblash qismi.
*   **Kassa oynasi (POS):** Kategoriyalarga ajratilgan mahsulotlar ro'yxatidan keraklilari tanlanadi, savatga qo'shiladi va umumiy summa hisoblanadi (Naqd, Karta yoki Qarz shaklida).
*   **Avtomatik chegirish:** Savdo tasdiqlanishi bilan sotilgan mahsulotlar Tayyor mahsulotlar omboridan darhol ayirib tashlanadi.
*   **Sotuvchini biriktirish:** Sotuv jarayonida yuqoridagi smena va sotuvchi (Xodim) menyusidan hozir qaysi xodim ishlayotgani tanlanadi.
*   **Ishbay (Piecework) va Hisobot:** Sotuv amalga oshgach, sotilgan har bir dona mahsulot uchun belgilangan ish haqi (ishbay summasi) avtomatik hisoblanib, tanlangan sotuvchining o'sha kundagi/smenadagi **DailyReport (Kunlik hisobotiga)** yozib qo'yiladi.

---

## 6. Kassa yopish va Hisobotlar
*   **Smenani yopish:** Smena oxirida sotuvchi "Smenani yopish" tugmasini bosadi.
*   **Chek/Hisobot:** Tizim shu smena davomida faqatgina shu sotuvchi tomonidan qilingan barcha savdolarni, sotilgan mahsulotlar sonini va uning ishlagan ishbay pulini jamlab, hisobot (chek) shaklida ekranga chiqarib beradi va chop etishga tayyorlaydi.

---
**Xulosa:** Tizim "Xom ashyo -> Retsept -> Ishlab chiqarish (kutish bilan) -> Tayyor mahsulot -> Sotuv -> Xodim maoshi" zanjirini to'liq va uzluksiz, bir-biriga bog'langan holda ta'minlaydi.
