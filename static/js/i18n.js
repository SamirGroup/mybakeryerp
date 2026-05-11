/**
 * BakeryERP — Client-side i18n (v2)
 * Supports: uz (O'zbek Latin), uz-cyrl (O'zbek Kirill), ru (Русский)
 *
 * Usage in templates:
 *   <span data-i18n="key">Default</span>
 *   <input data-i18n-placeholder="key">
 *   <option data-i18n="key">Default</option>
 *   <button data-i18n="key">Default</button>
 */

const TRANSLATIONS = {
  // ─────────────────────────────────────────────────────────
  // UZBEK LATIN
  // ─────────────────────────────────────────────────────────
  uz: {
    // Navigation
    "tabx1": "O'tkazmalar",
    "tabx2": "Qoldiqlar (Grid)",
    "nav_dashboard": "Boshqaruv paneli",
    "nav_production": "Ishlab chiqarish",
    "nav_sales": "Sotuv",
    "nav_branches": "Filiallar",
    "nav_accounting": "Buxgalteriya",
    "nav_hr": "HR Bo'limi",
    "nav_products": "Mahsulotlar",
    "nav_admin": "Foydalanuvchilar",

    // Dashboard
    today_revenue: "Bugungi daromad",
    products_produced: "Ishlab chiqarilgan",
    total_sales: "Jami sotuv",
    on_shift: "Bugun smenada",
    completed_transactions: "Bajarilgan operatsiyalar",
    active_employees: "Faol xodimlar",
    revenue_expenses: "Daromad va xarajatlar (oylik)",
    financial_summary: "Moliyaviy xulosa",
    total_cash: "Jami kassa qoldig'i",
    debtors: "Qarzdorlar (bizga qarashlilар)",
    creditors: "Kreditorlar (biz qarzdormiz)",
    top_products: "Eng ko'p sotiladigan mahsulotlar",
    from_yesterday: "Kechadan o'zgarish",
    yesterday_label: "Kecha",
    // chart labels
    week_1: "1-hafta",
    week_2: "2-hafta",
    week_3: "3-hafta",
    week_4: "4-hafta",
    units_sold: "Sotilgan dona",

    // Production
    production_warehouse: "Ishlab chiqarish va ombor",
    daily_production: "Kunlik ishlab chiqarish",
    raw_materials_wh: "Xom ashyo ombori",
    finished_goods: "Tayyor mahsulotlar",
    log_new_production: "Yangi ishlab chiqarishni qayd etish",
    select_product: "Mahsulotni tanlang",
    quantity_pieces: "Miqdori (dona/non)",
    baker_name: "Novvoy ismi (smena)",
    baker_placeholder: "Masalan: Ali (Kunduzgi smena)",
    save_log: "Ishlab chiqarishni saqlash",
    recent_logs: "So'nggi ishlab chiqarish qaydlari",
    date: "Sana",
    quantity: "Miqdori",
    baker: "Novvoy",
    no_recent_logs: "So'nggi qaydlar yo'q",
    raw_materials_stock: "Xom ashyo qoldig'i",
    material: "Xom ashyo",
    stock_left: "Qolgan miqdor",
    unit: "O'lchov birligi",
    status: "Holat",
    low_stock: "Oz qoldi",
    good: "Yaxshi",
    fg_inventory: "Tayyor mahsulotlar (Qoldiq)",
    current_stock: "Joriy qoldiq",
    no_finished: "Omborida tayyor mahsulotlar yo'q",
    no_materials: "Xom ashyolar yo'q",
    pieces: "dona",

    // Product Management
    product_mgmt: "Mahsulotlarni boshqarish",
    add_new_product: "Yangi mahsulot qo'shish",
    add_raw_material: "Yangi xom ashyo qo'shish",
    add_recipe: "Retsept qo'shish",
    receive_material: "Xom ashyo qabul qilish",
    product_name: "Mahsulot nomi",
    selling_price: "Sotuv narxi (UZS)",
    material_name: "Xom ashyo nomi",
    measurement_unit: "O'lchov birligi",
    initial_stock: "Boshlang'ich qoldiq",
    select_product_recipe: "Retsept uchun mahsulot tanlang",
    batch_size: "Partiya hajmi (necha donaga)",
    ingredient: "Ingredient",
    amount_needed: "Zarur miqdor",
    add_ingredient: "Ingredient qo'shish",
    save_recipe: "Retseptni saqlash",
    all_products: "Barcha mahsulotlar",
    all_raw_materials: "Barcha xom ashyolar",
    price: "Narx",
    in_stock: "Qoldiq",
    actions: "Amallar",
    delete: "O'chirish",
    save: "Saqlash",

    // Sales / POS
    pos_title: "Sotuv nuqtasi (POS)",
    quick_sale: "Tezkor sotuv",
    payment_method: "To'lov usuli",
    cash: "Naqd pul",
    terminal: "Terminal",
    click_payme: "Click/Payme",
    complete_sale: "Sotuvni yakunlash",
    returns_brak: "Qaytarish / Brak",
    submit_return: "Qaytarishni saqlash",
    available_stock: "Mavjud qoldiq",
    nasiya_prohibited: "Nasiya (qarz) qat'iyan taqiqlanadi.",
    reason_brak: "Brak (Yaramas)",
    reason_unsold: "Sotilmagan",
    no_stock: "Qoldiq yo'q",

    // Branches
    branches_title: "Filiallar (Sotuv nuqtalari)",
    send_to_branch: "Filiалga yuborish (Nakладная)",
    select_branch: "Filialni tanlang",
    create_waybill: "Yo'l varaqasi yaratish",
    recent_transfers: "So'nggi o'tkazmalar",
    branch: "Filial",
    in_transit: "Yo'lda",
    received: "Qabul qilindi",
    receive: "Qabul qilish",
    no_transfers: "O'tkazmalar yo'q",
    branch_inventories: "Filial qoldiqlari (Ostatka)",
    no_branches: "Filiallar yo'q",
    no_branches_desc: "Yangi filial qo'shish uchun Sozlamalar bo'limiga o'ting.",
    total_branches: "Filiallar soni",
    total_stock: "Filiallar qoldig'i",
    new_transfer: "Yangi o'tkazma",
    transfer_history: "O'tkazmalar tarixi",
    "management": "Sozlamalar",
    "details": "Tafsilotlar",

    // Accounting
    accounting_title: "Buxgalteriya va moliya",
    record_expense: "Xarajatni qayd etish",
    amount: "Summa",
    from_register: "Kassadan",
    category: "Kategoriya",
    description: "Tavsif",
    expense_placeholder: "Masalan: Elektr uchun to'lov",
    transfer_funds: "Mablag' o'tkazish",
    from: "Dan",
    to: "Ga",
    execute_transfer: "O'tkazmani bajarish",
    recent_ledger: "So'nggi operatsiyalar (Журнал)",
    income: "Daromad",
    expense: "Xarajat",
    transfer: "O'tkazma",
    register: "Kassa",
    no_transactions: "So'nggi operatsiyalar yo'q",
    no_registers: "Kassalar yo'q",
    status_active: "Faol",
    type: "Tur",
    supplier_payment: "Ta'minotchi to'lovi",

    // HR
    hr_title: "Kadrlar bo'limi",
    active_emps: "Faol xodimlar",
    today: "Bugun",
    emp_roster: "Xodimlar ro'yxati",
    name: "Ismi",
    position: "Lavozimi",
    piecework: "Ishbay",
    fixed_salary: "Oylik maosh",
    issue_advance: "Avans berish",
    employee: "Xodim",
    give_advance: "Avans berish",
    recent_advances: "So'nggi avanslar",
    no_employees: "Ma'lumotlar bazasida xodimlar yo'q",
    no_advances: "So'nggi avanslar yo'q",
    status_vacation: "Ta'tilda",
    status_left: "Ketgan",

    // Select option placeholders
    opt_select: "-- Tanlang --",
    opt_select_product: "-- Mahsulotni tanlang --",
    opt_select_branch: "-- Filialni tanlang --",
    opt_select_employee: "-- Xodimni tanlang --",

    // Language switcher
    language: "Til",

    // Setup / accounting
    setup: "Sozlamalar",
    add_register: "Yangi kassa qo'shish",
    register_name: "Kassa nomi",
    register_name_placeholder: "Masalan: Bosh kassa, Terminal",
    initial_balance: "Boshlang'ich qoldiq (UZS)",
    add_category: "Xarajat kategoriyasi qo'shish",
    category_name: "Kategoriya nomi",
    category_placeholder: "Masalan: Elektr, Un, Yoqilg'i",
    add_supplier: "Ta'minotchi qo'shish",
    supplier_name: "Ta'minotchi nomi",
    supplier_placeholder: "Masalan: Toshkent Un Zavodi",
    contact_info: "Aloqa ma'lumotlari",
    contact_placeholder: "+998 90 000 00 00",
    existing: "Mavjud",
    no_categories: "Kategoriyalar yo'q",
    no_suppliers: "Ta'minotchilar yo'q",
    no_registers_hint: "Avval kassalar qo'shing (Sozlamalar)",
    suppliers: "Ta'minotchilar",

    // Branches
    add_branch: "Yangi filial qo'shish",
    branch_name: "Filial nomi",
    branch_name_placeholder: "Masalan: Shahar markazi filiali",
    branch_address: "Manzil",
    branch_address_placeholder: "Ko'cha, uy raqami",
    responsible_person: "Mas'ul shaxs",
    responsible_placeholder: "Mas'ul shaxs ismi",
    no_branches_hint: "Avval filial qo'shing (3-tab)",

    // HR
    add_employee: "Yangi xodim qo'shish",
    total_staff: "Jami xodimlar",
    phone_label: "Telefon",
    date_joined: "Qo'shilgan sana",
    is_piecework_label: "Ishbay to'lov (novvoylar uchun)",
    base_salary: "Oylik maosh (UZS)",
    piecework_rate: "Bir dona uchun to'lov (UZS)",
    full_name_placeholder: "To'liq ismi sharifingiz",
    pos_baker: "Novvoy",
    pos_seller: "Sotuvchi",
    pos_driver: "Haydovchi",
    pos_guard: "Qorovul",
    pos_manager: "Boshqaruvchi",
    pos_cook: "Oshpaz",
    pos_accountant: "Buxgalter",

    // Accounting sub-menu
    acc_overview: "Ko'rinish",
    acc_cash: "Kassa",
    acc_ledger: "Jurnal",
    acc_balance: "Sinov balansi",
    acc_coa: "Hisoblar rejasi",
    acc_manual: "Qo'lda jurnal",
    acc_settings: "Sozlamalar",

    // HR extended
    hr_shifts: "Smenalar",
    hr_daily_report: "Kunlik hisobot",
    hr_add_report: "Hisobot qo'shish",
    hr_edit_emp: "Xodimni tahrirlash",
    hr_kpi: "KPI / Nagruzka",
    hr_attendance: "Davomat",
    hr_present: "Keldi",
    hr_absent: "Kelmadi",
    hr_check_in: "Kelgan vaqt",
    hr_check_out: "Ketgan vaqt",
    hr_hours_worked: "Ishlagan soat",
    hr_units_produced: "Ishlab chiqargan (dona)",
    hr_target: "Nagruzka (maqsad)",
    hr_piecework_earn: "Ishbay daromad",

    // Production extended
    prod_process: "Jarayon",
    prod_timer: "Timer (daqiqa)",
    prod_batches: "Partiya soni",
    prod_start: "Ishlab chiqarishni boshlash",
    prod_done: "Tayyor!",
    prod_active: "Faol jarayonlar",

    // Sales extended
    sale_shift: "Smena",
    sale_confirm: "Sotuvni tasdiqlash",
    sale_add_item: "Mahsulot qo'shish",
    sale_close_shift: "Smenani yopish",
    sale_shift_summary: "Smena xulosasi",
    sale_filter: "Filtrlash",
    sale_print: "Chop etish",
    sale_export: "Excel yuklab olish",
  },

  // ─────────────────────────────────────────────────────────
  // UZBEK CYRILLIC
  // ─────────────────────────────────────────────────────────
  "uz-cyrl": {
    "tabx1": "Ўтказмалар",
    "tabx2": "Қолдиқлар (Грид)",
    nav_dashboard: "Бошқарув панели",
    nav_production: "Ишлаб чиқариш",
    nav_sales: "Сотув",
    nav_branches: "Филиаллар",
    nav_accounting: "Бухгалтерия",
    nav_hr: "Кадрлар бўлими",
    nav_products: "Маҳсулотлар",
    nav_admin: "Фойдаланувчилар",
    today_revenue: "Бугунги даромад",
    products_produced: "Ишлаб чиқарилган",
    total_sales: "Жами сотув",
    on_shift: "Бугун сменада",
    completed_transactions: "Бажарилган операциялар",
    active_employees: "Фаол ходимлар",
    revenue_expenses: "Даромад ва харажатлар (ойлик)",
    financial_summary: "Молиявий хулоса",
    total_cash: "Жами касса қолдиғи",
    debtors: "Қарздорлар",
    creditors: "Кредиторлар",
    top_products: "Энг кўп сотиладиган маҳсулотлар",
    from_yesterday: "Кечадан ўзгариш",
    yesterday_label: "Кеча",
    week_1: "1-ҳафта",
    week_2: "2-ҳафта",
    week_3: "3-ҳафта",
    week_4: "4-ҳафта",
    units_sold: "Сотилган дона",
    production_warehouse: "Ишлаб чиқариш ва омбор",
    daily_production: "Кунлик ишлаб чиқариш",
    raw_materials_wh: "Хом ашё омбори",
    finished_goods: "Тайёр маҳсулотлар",
    log_new_production: "Янги ишлаб чиқаришни қайд этиш",
    select_product: "Маҳсулотни танланг",
    quantity_pieces: "Миқдори (дона/нон)",
    baker_name: "Новвой исми (смена)",
    baker_placeholder: "Масалан: Али (Кундузги смена)",
    save_log: "Ишлаб чиқаришни сақлаш",
    recent_logs: "Сўнгги ишлаб чиқариш қайдлари",
    date: "Сана",
    quantity: "Миқдори",
    baker: "Новвой",
    no_recent_logs: "Сўнгги қайдлар йўқ",
    raw_materials_stock: "Хом ашё қолдиғи",
    material: "Хом ашё",
    stock_left: "Қолган миқдор",
    unit: "Ўлчов бирлиги",
    status: "Ҳолат",
    low_stock: "Оз қолди",
    good: "Яхши",
    fg_inventory: "Тайёр маҳсулотлар (Қолдиқ)",
    current_stock: "Жорий қолдиқ",
    no_finished: "Омборида тайёр маҳсулотлар йўқ",
    no_materials: "Хом ашёлар йўқ",
    pieces: "дона",
    product_mgmt: "Маҳсулотларни бошқариш",
    add_new_product: "Янги маҳсулот қўшиш",
    add_raw_material: "Янги хом ашё қўшиш",
    add_recipe: "Рецепт қўшиш",
    receive_material: "Хом ашё қабул қилиш",
    product_name: "Маҳсулот номи",
    selling_price: "Сотув нархи (UZS)",
    material_name: "Хом ашё номи",
    measurement_unit: "Ўлчов бирлиги",
    initial_stock: "Бошланғич қолдиқ",
    select_product_recipe: "Рецепт учун маҳсулот танланг",
    batch_size: "Партия ҳажми",
    ingredient: "Ингредиент",
    amount_needed: "Зарур миқдор",
    add_ingredient: "Ингредиент қўшиш",
    save_recipe: "Рецептни сақлаш",
    all_products: "Барча маҳсулотлар",
    all_raw_materials: "Барча хом ашёлар",
    price: "Нарх",
    in_stock: "Қолдиқ",
    actions: "Амаллар",
    delete: "Ўчириш",
    save: "Сақлаш",
    pos_title: "Сотув нуқтаси (POS)",
    quick_sale: "Тезкор сотув",
    payment_method: "Тўлов усули",
    cash: "Нақд пул",
    terminal: "Терминал",
    click_payme: "Click/Payme",
    complete_sale: "Сотувни якунлаш",
    returns_brak: "Қайтариш / Брак",
    submit_return: "Қайтаришни сақлаш",
    available_stock: "Мавжуд қолдиқ",
    nasiya_prohibited: "Насия (қарз) қатъиян тақиқланади.",
    reason_brak: "Брак (Ярамас)",
    reason_unsold: "Сотилмаган",
    no_stock: "Қолдиқ йўқ",
    branches_title: "Филиаллар (Сотув нуқталари)",
    send_to_branch: "Филиалга юбориш (Накладная)",
    select_branch: "Филиални танланг",
    create_waybill: "Йўл варақаси яратиш",
    recent_transfers: "Сўнгги ўтказмалар",
    branch: "Филиал",
    in_transit: "Йўлда",
    received: "Қабул қилинди",
    receive: "Қабул қилиш",
    no_transfers: "Ўтказмалар йўқ",
    branch_inventories: "Филиал қолдиқлари (Остатка)",
    no_branches: "Филиаллар йўқ",
    no_branches_desc: "Янги филиал қўшиш учун Созламалар бўлимига ўтинг.",
    total_branches: "Филиаллар сони",
    total_stock: "Филиаллар қолдиғи",
    new_transfer: "Янги ўтказма",
    transfer_history: "Ўтказмалар тарихи",
    management: "Созламалар",
    details: "Тафсилотлар",
    accounting_title: "Бухгалтерия ва молия",
    record_expense: "Харажатни қайд этиш",
    amount: "Сумма",
    from_register: "Кассадан",
    category: "Категория",
    description: "Тавсиф",
    expense_placeholder: "Масалан: Электр учун тўлов",
    transfer_funds: "Маблағ ўтказиш",
    from: "Дан",
    to: "Га",
    execute_transfer: "Ўтказмани бажариш",
    recent_ledger: "Сўнгги операциялар (Журнал)",
    income: "Даромад",
    expense: "Харажат",
    transfer: "Ўтказма",
    register: "Касса",
    no_transactions: "Сўнгги операциялар йўқ",
    no_registers: "Кассалар йўқ",
    status_active: "Фаол",
    type: "Тур",
    supplier_payment: "Таъминотчи тўлови",
    hr_title: "Кадрлар бўлими",
    active_emps: "Фаол ходимлар",
    today: "Бугун",
    emp_roster: "Ходимлар рўйхати",
    name: "Исми",
    position: "Лавозими",
    piecework: "Ишбай",
    fixed_salary: "Ойлик маош",
    issue_advance: "Аванс бериш",
    employee: "Ходим",
    give_advance: "Аванс бериш",
    recent_advances: "Сўнгги авансlar",
    no_employees: "Маълумотлар базасида ходимлар йўқ",
    no_advances: "Сўнгги авансlar йўқ",
    status_vacation: "Та'тилда",
    status_left: "Кетган",
    opt_select: "-- Танланг --",
    opt_select_product: "-- Маҳсулотни танланг --",
    opt_select_branch: "-- Филиални танланг --",
    opt_select_employee: "-- Ходимни танланг --",
    language: "Тил",

    // Setup / accounting
    setup: "Созламалар",
    add_register: "Янги касса қўшиш",
    register_name: "Касса номи",
    register_name_placeholder: "Масалан: Бош касса, Терминал",
    initial_balance: "Бошланғич қолдиқ (UZS)",
    add_category: "Харажат категорияси қўшиш",
    category_name: "Категория номи",
    category_placeholder: "Масалан: Электр, Ун, Ёқилғи",
    add_supplier: "Таъминотчи қўшиш",
    supplier_name: "Таъминотчи номи",
    supplier_placeholder: "Масалан: Тошкент Ун Заводи",
    contact_info: "Алоқа маълумотлари",
    contact_placeholder: "+998 90 000 00 00",
    existing: "Мавжуд",
    no_categories: "Категориялар йўқ",
    no_suppliers: "Таъминотчилар йўқ",
    no_registers_hint: "Аввал кассалар қўшинг (Созламалар)",
    suppliers: "Таъминотчилар",
    add_branch: "Янги филиал қўшиш",
    branch_name: "Филиал номи",
    branch_name_placeholder: "Масалан: Шаҳар маркази филиали",
    branch_address: "Манзил",
    branch_address_placeholder: "Кўча, уй рақами",
    responsible_person: "Масъул шахс",
    responsible_placeholder: "Масъул шахс исми",
    no_branches_hint: "Аввал филиал қўшинг (3-таб)",
    add_employee: "Янги ходим қўшиш",
    total_staff: "Жами ходимлар",
    phone_label: "Телефон",
    date_joined: "Қўшилган сана",
    is_piecework_label: "Ишбай тўлов (новвойлар учун)",
    base_salary: "Ойлик маош (UZS)",
    piecework_rate: "Бир дона учун тўлов (UZS)",
    full_name_placeholder: "Тўлиқ исми шарифингиз",
    pos_baker: "Новвой",
    pos_seller: "Сотувчи",
    pos_driver: "Ҳайдовчи",
    pos_guard: "Қоровул",
    pos_manager: "Бошқарувчи",
    pos_cook: "Ошпаз",
    pos_accountant: "Бухгалтер",
    acc_overview: "Кўриниш",
    acc_cash: "Касса",
    acc_ledger: "Журнал",
    acc_balance: "Синов баланс",
    acc_coa: "Ҳисоблар режаси",
    acc_manual: "Қўлда журнал",
    acc_settings: "Созламалар",
    hr_shifts: "Сменалар",
    hr_daily_report: "Кунлик ҳисобот",
    hr_add_report: "Ҳисобот қўшиш",
    hr_edit_emp: "Ходимни таҳрирлаш",
    hr_kpi: "KPI / Нагрузка",
    hr_attendance: "Даомат",
    hr_present: "Келди",
    hr_absent: "Келмади",
    hr_check_in: "Келган вақт",
    hr_check_out: "Кетган вақт",
    hr_hours_worked: "Ишлаган соат",
    hr_units_produced: "Ишлаб чиқарган (дона)",
    hr_target: "Нагрузка (мақсад)",
    hr_piecework_earn: "Ишбай даромад",
    prod_process: "Жараён",
    prod_timer: "Таймер (дақиқа)",
    prod_batches: "Партия сони",
    prod_start: "Ишлаб чиқаришни бошлаш",
    prod_done: "Тайёр!",
    prod_active: "Фаол жараёнлар",
    sale_shift: "Смена",
    sale_confirm: "Сотувни тасдиқлаш",
    sale_add_item: "Маҳсулот қўшиш",
    sale_close_shift: "Сменани ёпиш",
    sale_shift_summary: "Смена хулосаси",
    sale_filter: "Фильтр",
    sale_print: "Чоп этиш",
    sale_export: "Excel юклаб олиш",
  },
  // ─────────────────────────────────────────────────────────
  ru: {
    "tabx1": "Переводы",
    "tabx2": "Сетка остатков",
    "nav_dashboard": "Панель управления",
    nav_production: "Производство",
    nav_sales: "Продажи",
    nav_branches: "Филиалы",
    nav_accounting: "Бухгалтерия",
    nav_hr: "Отдел кадров",
    nav_products: "Продукты",
    nav_admin: "Пользователи",
    today_revenue: "Выручка за сегодня",
    products_produced: "Произведено продуктов",
    total_sales: "Всего продаж",
    on_shift: "На смене сегодня",
    completed_transactions: "Завершённые операции",
    active_employees: "Активные сотрудники",
    revenue_expenses: "Доходы и расходы (ежемесячно)",
    financial_summary: "Финансовая сводка",
    total_cash: "Общий остаток по кассам",
    debtors: "Дебиторы (нам должны)",
    creditors: "Кредиторы (мы должны)",
    top_products: "Лучшие продукты по продажам",
    from_yesterday: "Изменение к вчера",
    yesterday_label: "Вчера",
    week_1: "Неделя 1",
    week_2: "Неделя 2",
    week_3: "Неделя 3",
    week_4: "Неделя 4",
    units_sold: "Продано штук",
    production_warehouse: "Производство и склад",
    daily_production: "Ежедневное производство",
    raw_materials_wh: "Склад сырья",
    finished_goods: "Готовая продукция",
    log_new_production: "Записать новое производство",
    select_product: "Выберите продукт",
    quantity_pieces: "Количество (штук/буханок)",
    baker_name: "Имя пекаря (смена)",
    baker_placeholder: "Напр.: Али (Дневная смена)",
    save_log: "Сохранить журнал производства",
    recent_logs: "Последние записи производства",
    date: "Дата",
    quantity: "Количество",
    baker: "Пекарь",
    no_recent_logs: "Последних записей нет",
    raw_materials_stock: "Запасы сырья",
    material: "Материал",
    stock_left: "Остаток на складе",
    unit: "Единица измерения",
    status: "Статус",
    low_stock: "Мало запасов",
    good: "Хорошо",
    fg_inventory: "Склад готовой продукции (Остаток)",
    current_stock: "Текущий остаток",
    no_finished: "Готовой продукции на складе нет",
    no_materials: "Сырья нет",
    pieces: "шт.",
    product_mgmt: "Управление продуктами",
    add_new_product: "Добавить новый продукт",
    add_raw_material: "Добавить сырьё",
    add_recipe: "Добавить рецепт",
    receive_material: "Принять сырьё",
    product_name: "Название продукта",
    selling_price: "Цена продажи (UZS)",
    material_name: "Название материала",
    measurement_unit: "Единица измерения",
    initial_stock: "Начальный остаток",
    select_product_recipe: "Выберите продукт для рецепта",
    batch_size: "Размер партии",
    ingredient: "Ингредиент",
    amount_needed: "Необходимое количество",
    add_ingredient: "Добавить ингредиент",
    save_recipe: "Сохранить рецепт",
    all_products: "Все продукты",
    all_raw_materials: "Всё сырьё",
    price: "Цена",
    in_stock: "Остаток",
    actions: "Действия",
    delete: "Удалить",
    save: "Сохранить",
    pos_title: "Кассовый терминал (POS)",
    quick_sale: "Быстрая продажа",
    payment_method: "Способ оплаты",
    cash: "Наличные",
    terminal: "Терминал",
    click_payme: "Click/Payme",
    complete_sale: "Завершить продажу",
    returns_brak: "Возврат / Брак",
    submit_return: "Оформить возврат",
    available_stock: "Доступный остаток",
    nasiya_prohibited: "Продажа в кредит (Насия) строго запрещена.",
    reason_brak: "Брак (непригодный)",
    reason_unsold: "Непроданный",
    no_stock: "Нет остатков",
    branches_title: "Филиалы (Точки продаж)",
    send_to_branch: "Отправить в филиал (Накладная)",
    select_branch: "Выберите филиал",
    create_waybill: "Создать накладную (Перемещение)",
    recent_transfers: "Последние перемещения",
    branch: "Филиал",
    in_transit: "В пути",
    received: "Получено",
    receive: "Принять",
    no_transfers: "Перемещений нет",
    branch_inventories: "Остатки по филиалам",
    no_branches: "Филиалов нет",
    no_branches_desc: "Перейдите в Настройки, чтобы добавить новый филиал.",
    total_branches: "Кол-во филиалов",
    total_stock: "Остаток в филиалах",
    new_transfer: "Новое перемещение",
    transfer_history: "История перемещений",
    management: "Настройки",
    details: "Детали",
    accounting_title: "Бухгалтерия и финансы",
    record_expense: "Записать расход",
    amount: "Сумма",
    from_register: "Из кассы",
    category: "Категория",
    description: "Описание",
    expense_placeholder: "Напр.: Оплата электроэнергии",
    transfer_funds: "Перевод средств",
    from: "Откуда",
    to: "Куда",
    execute_transfer: "Выполнить перевод",
    recent_ledger: "Последние операции (Журнал)",
    income: "Доход",
    expense: "Расход",
    transfer: "Перевод",
    register: "Касса",
    no_transactions: "Последних операций нет",
    no_registers: "Кассы не определены",
    status_active: "Активен",
    type: "Тип",
    supplier_payment: "Оплата поставщику",
    hr_title: "Управление персоналом",
    active_emps: "Активные сотрудники",
    today: "Сегодня",
    emp_roster: "Список сотрудников",
    name: "Имя",
    position: "Должность",
    piecework: "Сдельная оплата",
    fixed_salary: "Фиксированная зарплата",
    issue_advance: "Выдать аванс",
    employee: "Сотрудник",
    give_advance: "Выдать аванс",
    recent_advances: "Последние авансы",
    no_employees: "Сотрудников в базе нет",
    no_advances: "Последних авансов нет",
    status_vacation: "В отпуске",
    status_left: "Уволен",
    opt_select: "-- Выберите --",
    opt_select_product: "-- Выберите продукт --",
    opt_select_branch: "-- Выберите филиал --",
    opt_select_employee: "-- Выберите сотрудника --",
    language: "Язык",

    // Setup / accounting
    setup: "Настройки",
    add_register: "Добавить кассу",
    register_name: "Название кассы",
    register_name_placeholder: "Напр.: Главная касса, Терминал",
    initial_balance: "Начальный остаток (UZS)",
    add_category: "Добавить категорию расходов",
    category_name: "Название категории",
    category_placeholder: "Напр.: Электроэнергия, Мука, Топливо",
    add_supplier: "Добавить поставщика",
    supplier_name: "Название поставщика",
    supplier_placeholder: "Напр.: Ташкентский мукомольный завод",
    contact_info: "Контактная информация",
    contact_placeholder: "+998 90 000 00 00",
    existing: "Существующие",
    no_categories: "Категорий нет",
    no_suppliers: "Поставщиков нет",
    no_registers_hint: "Сначала добавьте кассу (Настройки)",
    suppliers: "Поставщики",
    add_branch: "Добавить филиал",
    branch_name: "Название филиала",
    branch_name_placeholder: "Напр.: Центральный филиал",
    branch_address: "Адрес",
    branch_address_placeholder: "Улица, номер дома",
    responsible_person: "Ответственное лицо",
    responsible_placeholder: "Имя ответственного",
    no_branches_hint: "Сначала добавьте филиал (вкладка 3)",
    add_employee: "Добавить нового сотрудника",
    total_staff: "Всего сотрудников",
    phone_label: "Телефон",
    date_joined: "Дата принятия",
    is_piecework_label: "Сдельная оплата (для пекарей)",
    base_salary: "Фиксированная зарплата (UZS)",
    piecework_rate: "Ставка за единицу (UZS)",
    full_name_placeholder: "Полное имя сотрудника",
    pos_baker: "Пекарь",
    pos_seller: "Продавец",
    pos_driver: "Водитель",
    pos_guard: "Охранник",
    pos_manager: "Управляющий",
    pos_cook: "Повар",
    pos_accountant: "Бухгалтер",

    // Accounting sub-menu
    acc_overview: "Обзор",
    acc_cash: "Касса",
    acc_ledger: "Журнал",
    acc_balance: "Пробный баланс",
    acc_coa: "План счетов",
    acc_manual: "Ручной журнал",
    acc_settings: "Настройки",

    // HR extended
    hr_shifts: "Смены",
    hr_daily_report: "Ежедневный отчёт",
    hr_add_report: "Добавить отчёт",
    hr_edit_emp: "Редактировать сотрудника",
    hr_kpi: "KPI / Нагрузка",
    hr_attendance: "Посещаемость",
    hr_present: "Пришёл",
    hr_absent: "Не пришёл",
    hr_check_in: "Время прихода",
    hr_check_out: "Время ухода",
    hr_hours_worked: "Отработано часов",
    hr_units_produced: "Произведено (шт.)",
    hr_target: "Нагрузка (план)",
    hr_piecework_earn: "Сдельный заработок",

    // Production extended
    prod_process: "Процесс",
    prod_timer: "Таймер (минуты)",
    prod_batches: "Кол-во партий",
    prod_start: "Начать производство",
    prod_done: "Готово!",
    prod_active: "Активные процессы",

    // Sales extended
    sale_shift: "Смена",
    sale_confirm: "Подтвердить продажу",
    sale_add_item: "Добавить товар",
    sale_close_shift: "Закрыть смену",
    sale_shift_summary: "Итог смены",
    sale_filter: "Фильтр",
    sale_print: "Печать",
    sale_export: "Скачать Excel",
  },
};

// ─── Language engine ────────────────────────────────────────────────────────
function getCurrentLang() {
  return localStorage.getItem('erp_lang') || localStorage.getItem('erp_gt_lang') || 'uz';
}

function t(key) {
  var lang = getCurrentLang();
  return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) ||
         (TRANSLATIONS['uz'] && TRANSLATIONS['uz'][key]) || key;
}

function applyTranslations() {
  var lang = getCurrentLang();
  // ru tanlanganda Google Translate o'zi tarjima qiladi, data-i18n ni o'zgartirmaymiz
  if (lang === 'ru') {
    document.documentElement.lang = 'uz';
    document.querySelectorAll('.lang-btn').forEach(function(btn) {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    return;
  }

  var dict = TRANSLATIONS[lang] || TRANSLATIONS['uz'];

  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.getAttribute('data-i18n');
    var val = dict[key] || (TRANSLATIONS['uz'] && TRANSLATIONS['uz'][key]) || key;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = val;
    } else {
      // Ichki <i>, <span> kabi elementlarni saqlab, faqat text node larni yangilaymiz
      var hasChildElements = Array.from(el.childNodes).some(function(n) { return n.nodeType === 1; });
      if (hasChildElements) {
        // Oxirgi text node ni topib yangilaymiz, yo'q bo'lsa yaratamiz
        var lastText = null;
        el.childNodes.forEach(function(n) { if (n.nodeType === 3) lastText = n; });
        if (lastText) {
          lastText.textContent = ' ' + val;
        } else {
          el.appendChild(document.createTextNode(' ' + val));
        }
      } else {
        el.textContent = val;
      }
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
    var key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = dict[key] || (TRANSLATIONS['uz'] && TRANSLATIONS['uz'][key]) || key;
  });

  document.documentElement.lang = lang;

  document.querySelectorAll('.lang-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
}

function setLanguage(lang) {
  localStorage.setItem('erp_lang', lang);
  localStorage.setItem('erp_gt_lang', lang);
  applyTranslations();
}

// Run immediately + on DOM ready
applyTranslations();
document.addEventListener('DOMContentLoaded', applyTranslations);

// Chart.js labellarini tarjima qilish
// Google Translate canvas ni tarjima qila olmaydi,
// shuning uchun Chart yaratilganda labellar i18n orqali o'giriladi
(function() {
  if (typeof Chart === 'undefined') return;
  var _origRegister = Chart.register ? Chart.register.bind(Chart) : null;

  // Chart yaratilganda labellarni tarjima qilish
  var OrigChart = Chart;
  window.Chart = function(ctx, config) {
    if (config && config.data) {
      var lang = getCurrentLang();
      if (lang !== 'uz') {
        // labels massivini tarjima qilish
        if (Array.isArray(config.data.labels)) {
          config.data.labels = config.data.labels.map(function(lbl) {
            return t(lbl) !== lbl ? t(lbl) : lbl;
          });
        }
        // dataset label larni tarjima qilish
        if (Array.isArray(config.data.datasets)) {
          config.data.datasets.forEach(function(ds) {
            if (ds.label) ds.label = t(ds.label) !== ds.label ? t(ds.label) : ds.label;
          });
        }
      }
    }
    return new OrigChart(ctx, config);
  };
  // Statik metodlarni ko'chirish
  Object.keys(OrigChart).forEach(function(k) {
    try { window.Chart[k] = OrigChart[k]; } catch(e) {}
  });
  window.Chart.prototype = OrigChart.prototype;
})();
