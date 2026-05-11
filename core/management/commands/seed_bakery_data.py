from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounting import services as accounting_services
from accounting.models import (
    Account,
    CashRegister,
    ExpenseCategory,
    JournalEntry,
    JournalLine,
    Supplier,
    Transaction,
)
from branches.models import (
    Branch,
    BranchInventory,
    BranchSale,
    BranchSaleItem,
    Transfer,
    TransferItem,
)
from hr.models import AdvancePayment, Attendance, Employee, Payroll
from production.models import (
    FinishedGoodsInventory,
    Product,
    ProductionLog,
    RawMaterial,
    Recipe,
    RecipeItem,
)
from sales.models import ReturnLog, Sale, SaleItem


class Command(BaseCommand):
    help = (
        "Barcha bo‘limlar (dashboard, ishlab chiqarish, sotuv, filiallar, buxgalteriya, HR) "
        "uchun demo ma’lumot. GL jurnal bilan to‘liq ko‘rinish uchun kassa operatsiyalari "
        "accounting.services orqali yoziladi. Takroriy toza urish: --reset. "
        "Superuser bo‘lmasa, jurnal uchun '__seed_journal__' tizim foydalanuvchisi yaratiladi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data in business tables before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._clear_business_data()
            self.stdout.write(self.style.WARNING("Existing business data cleared."))

        raw_materials = self._seed_raw_materials()
        products = self._seed_products()
        self._seed_recipes(products, raw_materials)
        self._seed_finished_inventory(products)
        self._seed_production_logs(products)

        branches = self._seed_branches()
        self._seed_branch_inventory(branches, products)
        self._seed_transfers(branches, products)
        self._seed_branch_sales(branches, products)

        self._seed_pos_sales(products)
        self._seed_return_logs(products)

        accounting = self._seed_accounting()
        seed_user = self._get_seed_user()
        self._seed_accounting_with_gl(seed_user, accounting)
        employees = self._seed_employees()
        self._seed_attendance(employees)
        self._seed_advances(employees)
        self._seed_payroll(employees)

        self.stdout.write(self.style.SUCCESS("Bakery CRM demo data seeded successfully."))

    def _clear_business_data(self):
        BranchSaleItem.objects.all().delete()
        BranchSale.objects.all().delete()
        TransferItem.objects.all().delete()
        Transfer.objects.all().delete()
        BranchInventory.objects.all().delete()

        SaleItem.objects.all().delete()
        Sale.objects.all().delete()
        ReturnLog.objects.all().delete()

        JournalLine.objects.all().delete()
        JournalEntry.objects.all().delete()
        Transaction.objects.all().delete()

        ProductionLog.objects.all().delete()
        FinishedGoodsInventory.objects.all().delete()
        RecipeItem.objects.all().delete()
        Recipe.objects.all().delete()
        Product.objects.all().delete()
        RawMaterial.objects.all().delete()

        Supplier.objects.all().delete()
        ExpenseCategory.objects.all().delete()
        CashRegister.objects.all().delete()

        Payroll.objects.all().delete()
        AdvancePayment.objects.all().delete()
        Attendance.objects.all().delete()
        Employee.objects.all().delete()

        Branch.objects.all().delete()

    def _seed_raw_materials(self):
        materials = {
            "Premium un": {"unit": "kg", "stock": Decimal("4200.00")},
            "1-nav un": {"unit": "kg", "stock": Decimal("2800.00")},
            "Xamirturush": {"unit": "kg", "stock": Decimal("140.00")},
            "Tuz": {"unit": "kg", "stock": Decimal("320.00")},
            "Shakar": {"unit": "kg", "stock": Decimal("780.00")},
            "Osimlik yogi": {"unit": "liter", "stock": Decimal("950.00")},
            "Margarin": {"unit": "kg", "stock": Decimal("420.00")},
            "Sut": {"unit": "liter", "stock": Decimal("1100.00")},
            "Kunjut": {"unit": "kg", "stock": Decimal("90.00")},
            "Qora sedana": {"unit": "kg", "stock": Decimal("45.00")},
        }

        objects = {}
        for name, payload in materials.items():
            obj, _ = RawMaterial.objects.update_or_create(
                name=name,
                defaults={
                    "unit": payload["unit"],
                    "stock": payload["stock"],
                },
            )
            objects[name] = obj
        return objects

    def _seed_products(self):
        product_prices = {
            "Obi Non": Decimal("4500.00"),
            "Patir Non": Decimal("7000.00"),
            "Buxanka": Decimal("6000.00"),
            "Bulochka": Decimal("3500.00"),
            "Qatlama Non": Decimal("8000.00"),
        }

        objects = {}
        for name, price in product_prices.items():
            obj, _ = Product.objects.update_or_create(
                name=name,
                defaults={"price": price},
            )
            objects[name] = obj
        return objects

    def _seed_recipes(self, products, raw_materials):
        recipe_data = {
            "Obi Non": {
                "batch_size": 100,
                "items": {
                    "Premium un": Decimal("68.000"),
                    "Xamirturush": Decimal("1.100"),
                    "Tuz": Decimal("0.900"),
                    "Osimlik yogi": Decimal("1.200"),
                    "Qora sedana": Decimal("0.200"),
                },
            },
            "Patir Non": {
                "batch_size": 80,
                "items": {
                    "Premium un": Decimal("62.000"),
                    "Margarin": Decimal("4.500"),
                    "Tuz": Decimal("0.800"),
                    "Xamirturush": Decimal("1.000"),
                    "Kunjut": Decimal("0.400"),
                },
            },
            "Buxanka": {
                "batch_size": 120,
                "items": {
                    "1-nav un": Decimal("70.000"),
                    "Xamirturush": Decimal("1.500"),
                    "Tuz": Decimal("1.100"),
                    "Shakar": Decimal("1.200"),
                    "Sut": Decimal("8.000"),
                },
            },
            "Bulochka": {
                "batch_size": 150,
                "items": {
                    "1-nav un": Decimal("55.000"),
                    "Shakar": Decimal("5.000"),
                    "Margarin": Decimal("3.200"),
                    "Sut": Decimal("10.000"),
                    "Xamirturush": Decimal("1.300"),
                },
            },
            "Qatlama Non": {
                "batch_size": 70,
                "items": {
                    "Premium un": Decimal("50.000"),
                    "Margarin": Decimal("6.200"),
                    "Tuz": Decimal("0.900"),
                    "Kunjut": Decimal("0.500"),
                },
            },
        }

        for product_name, payload in recipe_data.items():
            recipe, _ = Recipe.objects.update_or_create(
                product=products[product_name],
                defaults={"batch_size": payload["batch_size"]},
            )
            RecipeItem.objects.filter(recipe=recipe).delete()
            for material_name, qty in payload["items"].items():
                RecipeItem.objects.create(
                    recipe=recipe,
                    raw_material=raw_materials[material_name],
                    quantity=qty,
                )

    def _seed_finished_inventory(self, products):
        stocks = {
            "Obi Non": 520,
            "Patir Non": 210,
            "Buxanka": 340,
            "Bulochka": 460,
            "Qatlama Non": 150,
        }

        for product_name, stock in stocks.items():
            FinishedGoodsInventory.objects.update_or_create(
                product=products[product_name],
                defaults={"stock": stock},
            )

    def _seed_production_logs(self, products):
        ProductionLog.objects.all().delete()
        logs = [
            ("Obi Non", 300, "Umar aka"),
            ("Patir Non", 120, "Shahzod"),
            ("Buxanka", 180, "Nodir"),
            ("Bulochka", 220, "Murod"),
            ("Qatlama Non", 90, "Umar aka"),
        ]
        for i, (product_name, quantity, baker_name) in enumerate(logs):
            log = ProductionLog.objects.create(
                product=products[product_name],
                quantity=quantity,
                baker_name=baker_name,
            )
            ProductionLog.objects.filter(pk=log.pk).update(
                date=timezone.now() - timedelta(days=i, hours=i + 1)
            )

    def _seed_branches(self):
        branch_data = [
            {
                "name": "Chilonzor filiali",
                "address": "Toshkent sh., Chilonzor 12-kvartal, 45-uy",
                "responsible_person": "Dilshod Rahimov",
            },
            {
                "name": "Yunusobod filiali",
                "address": "Toshkent sh., Yunusobod 7-mavze, 14-uy",
                "responsible_person": "Madina Jo'rayeva",
            },
            {
                "name": "Sergeli filiali",
                "address": "Toshkent sh., Sergeli 5-mavze, 22-uy",
                "responsible_person": "Farrux Karimov",
            },
        ]

        branches = {}
        for payload in branch_data:
            branch, _ = Branch.objects.update_or_create(
                name=payload["name"],
                defaults={
                    "address": payload["address"],
                    "responsible_person": payload["responsible_person"],
                },
            )
            branches[payload["name"]] = branch
        return branches

    def _seed_branch_inventory(self, branches, products):
        matrix = {
            "Chilonzor filiali": {
                "Obi Non": 140,
                "Patir Non": 70,
                "Buxanka": 85,
                "Bulochka": 120,
                "Qatlama Non": 40,
            },
            "Yunusobod filiali": {
                "Obi Non": 115,
                "Patir Non": 65,
                "Buxanka": 92,
                "Bulochka": 100,
                "Qatlama Non": 38,
            },
            "Sergeli filiali": {
                "Obi Non": 130,
                "Patir Non": 55,
                "Buxanka": 80,
                "Bulochka": 95,
                "Qatlama Non": 32,
            },
        }

        for branch_name, product_map in matrix.items():
            for product_name, stock in product_map.items():
                BranchInventory.objects.update_or_create(
                    branch=branches[branch_name],
                    product=products[product_name],
                    defaults={"stock": stock},
                )

    def _seed_transfers(self, branches, products):
        TransferItem.objects.all().delete()
        Transfer.objects.all().delete()

        received = Transfer.objects.create(
            branch=branches["Chilonzor filiali"],
            status="received",
            date_received=timezone.now(),
        )
        TransferItem.objects.bulk_create(
            [
                TransferItem(transfer=received, product=products["Obi Non"], quantity=120),
                TransferItem(transfer=received, product=products["Buxanka"], quantity=60),
                TransferItem(transfer=received, product=products["Bulochka"], quantity=80),
            ]
        )

        in_transit = Transfer.objects.create(
            branch=branches["Yunusobod filiali"],
            status="in_transit",
        )
        TransferItem.objects.bulk_create(
            [
                TransferItem(transfer=in_transit, product=products["Patir Non"], quantity=50),
                TransferItem(transfer=in_transit, product=products["Qatlama Non"], quantity=30),
            ]
        )

    def _seed_branch_sales(self, branches, products):
        BranchSaleItem.objects.all().delete()
        BranchSale.objects.all().delete()

        sale_templates = [
            (
                "Chilonzor filiali",
                [("Obi Non", 95), ("Patir Non", 35), ("Bulochka", 70)],
            ),
            (
                "Yunusobod filiali",
                [("Obi Non", 82), ("Buxanka", 44), ("Qatlama Non", 18)],
            ),
            (
                "Sergeli filiali",
                [("Obi Non", 88), ("Patir Non", 29), ("Buxanka", 41)],
            ),
        ]

        for i, (branch_name, items) in enumerate(sale_templates):
            branch_sale = BranchSale.objects.create(branch=branches[branch_name])
            total = Decimal("0.00")
            for product_name, qty in items:
                price = products[product_name].price
                BranchSaleItem.objects.create(
                    branch_sale=branch_sale,
                    product=products[product_name],
                    quantity=qty,
                    price_at_sale=price,
                )
                total += price * qty
            branch_sale.total_amount = total
            branch_sale.save(update_fields=["total_amount"])
            d = timezone.now().date() - timedelta(days=i * 4 + 1)
            BranchSale.objects.filter(pk=branch_sale.pk).update(date=d)

    def _seed_pos_sales(self, products):
        SaleItem.objects.all().delete()
        Sale.objects.all().delete()

        sales_templates = [
            ("cash", [("Obi Non", 24), ("Bulochka", 18)]),
            ("terminal", [("Patir Non", 12), ("Buxanka", 10)]),
            ("electronic", [("Obi Non", 20), ("Qatlama Non", 8)]),
            ("cash", [("Buxanka", 16), ("Bulochka", 30)]),
            ("terminal", [("Obi Non", 28), ("Patir Non", 9), ("Bulochka", 15)]),
        ]

        for idx, (payment_method, items) in enumerate(sales_templates):
            sale = Sale.objects.create(payment_method=payment_method)
            total = Decimal("0.00")
            for product_name, qty in items:
                price = products[product_name].price
                SaleItem.objects.create(
                    sale=sale,
                    product=products[product_name],
                    quantity=qty,
                    price_at_sale=price,
                )
                total += price * qty
            sale.total_amount = total
            sale.save(update_fields=["total_amount"])
            when = timezone.now() - timedelta(days=idx * 2, hours=idx + 2, minutes=idx * 7)
            Sale.objects.filter(pk=sale.pk).update(date=when)

    def _seed_return_logs(self, products):
        ReturnLog.objects.all().delete()
        ReturnLog.objects.bulk_create(
            [
                ReturnLog(
                    product=products["Obi Non"],
                    quantity=6,
                    reason="unsold",
                    notes="Kechki smenadan qolgan nonlar",
                ),
                ReturnLog(
                    product=products["Bulochka"],
                    quantity=4,
                    reason="brak",
                    notes="Pishirishda shakli buzilgan",
                ),
            ]
        )

    def _seed_accounting(self):
        """Kassa, kategoriya va ta’minotchilar — balanslar keyingi qadamda GL orqali to‘ldiriladi."""
        cash_register_names = [
            "Asosiy kassa",
            "Terminal",
            "Xarajat kassasi",
            "Main Cash",
            "CRM",
        ]
        categories = ["Xomashyo", "Kommunal tolov", "Transport", "Ish haqi"]
        suppliers = {
            "Toshkent Un Zavodi": Decimal("6200000.00"),
            "Sut Dunyosi MChJ": Decimal("1750000.00"),
            "Yog-Moy Savdo": Decimal("980000.00"),
        }

        registers = {}
        for name in cash_register_names:
            register, _ = CashRegister.objects.update_or_create(
                name=name,
                defaults={"balance": Decimal("0.00")},
            )
            registers[name] = register

        expense_categories = {}
        for name in categories:
            category, _ = ExpenseCategory.objects.update_or_create(name=name)
            expense_categories[name] = category

        supplier_objects = {}
        for name, debt in suppliers.items():
            supplier, _ = Supplier.objects.update_or_create(
                name=name,
                defaults={
                    "contact_info": "+998 90 000 00 00",
                    "debt": debt,
                },
            )
            supplier_objects[name] = supplier

        return {
            "registers": registers,
            "expense_categories": expense_categories,
            "suppliers": supplier_objects,
        }

    def _seed_employees(self):
        employee_data = [
            {
                "name": "Umar Normurodov",
                "phone": "+998901112233",
                "position": "Baker",
                "date_joined": "2023-03-10",
                "status": "active",
                "is_piecework": True,
                "base_salary": Decimal("0.00"),
                "piecework_rate": Decimal("450.00"),
            },
            {
                "name": "Shahzod Karimov",
                "phone": "+998933334455",
                "position": "Baker",
                "date_joined": "2024-01-15",
                "status": "active",
                "is_piecework": True,
                "base_salary": Decimal("0.00"),
                "piecework_rate": Decimal("420.00"),
            },
            {
                "name": "Madina Jo'rayeva",
                "phone": "+998977776655",
                "position": "Seller",
                "date_joined": "2022-11-01",
                "status": "active",
                "is_piecework": False,
                "base_salary": Decimal("3500000.00"),
                "piecework_rate": Decimal("0.00"),
            },
            {
                "name": "Dilshod Rahimov",
                "phone": "+998998887766",
                "position": "Branch Manager",
                "date_joined": "2021-09-21",
                "status": "active",
                "is_piecework": False,
                "base_salary": Decimal("5200000.00"),
                "piecework_rate": Decimal("0.00"),
            },
            {
                "name": "Nodir Tursunov",
                "phone": "+998911234567",
                "position": "Dough Master",
                "date_joined": "2023-07-07",
                "status": "active",
                "is_piecework": False,
                "base_salary": Decimal("4300000.00"),
                "piecework_rate": Decimal("0.00"),
            },
            {
                "name": "Farrux Karimov",
                "phone": "+998945556677",
                "position": "Courier",
                "date_joined": "2024-05-12",
                "status": "active",
                "is_piecework": False,
                "base_salary": Decimal("3200000.00"),
                "piecework_rate": Decimal("0.00"),
            },
            {
                "name": "Malika Usmonova",
                "phone": "+998936667788",
                "position": "Accountant",
                "date_joined": "2022-04-18",
                "status": "active",
                "is_piecework": False,
                "base_salary": Decimal("4800000.00"),
                "piecework_rate": Decimal("0.00"),
            },
            {
                "name": "Sardor Abduvaliyev",
                "phone": "+998909876543",
                "position": "Guard",
                "date_joined": "2021-12-02",
                "status": "vacation",
                "is_piecework": False,
                "base_salary": Decimal("2500000.00"),
                "piecework_rate": Decimal("0.00"),
            },
        ]

        employees = {}
        for payload in employee_data:
            employee, _ = Employee.objects.update_or_create(
                phone=payload["phone"],
                defaults={
                    "name": payload["name"],
                    "position": payload["position"],
                    "date_joined": payload["date_joined"],
                    "status": payload["status"],
                    "is_piecework": payload["is_piecework"],
                    "base_salary": payload["base_salary"],
                    "piecework_rate": payload["piecework_rate"],
                },
            )
            employees[payload["name"]] = employee

        return employees

    def _seed_attendance(self, employees):
        Attendance.objects.all().delete()
        Attendance.objects.bulk_create(
            [
                Attendance(
                    employee=employees["Umar Normurodov"],
                    check_in="06:00",
                    check_out="14:00",
                    shift="day",
                ),
                Attendance(
                    employee=employees["Shahzod Karimov"],
                    check_in="14:00",
                    check_out="22:00",
                    shift="night",
                ),
                Attendance(
                    employee=employees["Madina Jo'rayeva"],
                    check_in="08:00",
                    check_out="18:00",
                    shift="day",
                ),
                Attendance(
                    employee=employees["Dilshod Rahimov"],
                    check_in="09:00",
                    check_out="18:30",
                    shift="day",
                ),
            ]
        )

    def _seed_advances(self, employees):
        AdvancePayment.objects.all().delete()
        AdvancePayment.objects.bulk_create(
            [
                AdvancePayment(employee=employees["Umar Normurodov"], amount=Decimal("800000.00")),
                AdvancePayment(employee=employees["Madina Jo'rayeva"], amount=Decimal("500000.00")),
                AdvancePayment(employee=employees["Farrux Karimov"], amount=Decimal("400000.00")),
            ]
        )

    def _seed_payroll(self, employees):
        Payroll.objects.all().delete()
        month_anchor = timezone.now().date().replace(day=1)

        payroll_rows = [
            {
                "employee": employees["Umar Normurodov"],
                "base_pay": Decimal("0.00"),
                "piecework_pay": Decimal("5600000.00"),
                "bonus": Decimal("350000.00"),
                "penalty": Decimal("0.00"),
                "advance_deductions": Decimal("800000.00"),
            },
            {
                "employee": employees["Shahzod Karimov"],
                "base_pay": Decimal("0.00"),
                "piecework_pay": Decimal("4900000.00"),
                "bonus": Decimal("250000.00"),
                "penalty": Decimal("100000.00"),
                "advance_deductions": Decimal("0.00"),
            },
            {
                "employee": employees["Madina Jo'rayeva"],
                "base_pay": Decimal("3500000.00"),
                "piecework_pay": Decimal("0.00"),
                "bonus": Decimal("200000.00"),
                "penalty": Decimal("0.00"),
                "advance_deductions": Decimal("500000.00"),
            },
            {
                "employee": employees["Dilshod Rahimov"],
                "base_pay": Decimal("5200000.00"),
                "piecework_pay": Decimal("0.00"),
                "bonus": Decimal("300000.00"),
                "penalty": Decimal("0.00"),
                "advance_deductions": Decimal("0.00"),
            },
        ]

        for row in payroll_rows:
            net_paid = (
                row["base_pay"]
                + row["piecework_pay"]
                + row["bonus"]
                - row["penalty"]
                - row["advance_deductions"]
            )
            Payroll.objects.create(
                employee=row["employee"],
                month=month_anchor,
                base_pay=row["base_pay"],
                piecework_pay=row["piecework_pay"],
                bonus=row["bonus"],
                penalty=row["penalty"],
                advance_deductions=row["advance_deductions"],
                net_paid=net_paid,
            )

    def _get_seed_user(self):
        User = get_user_model()
        u = User.objects.filter(is_superuser=True).first()
        if u:
            return u
        u, created = User.objects.get_or_create(
            username='__seed_journal__',
            defaults={
                'is_active': True,
                'is_staff': False,
                'first_name': 'Demo jurnal',
            },
        )
        if created:
            u.set_unusable_password()
            u.save(update_fields=['password'])
        return u

    def _seed_accounting_with_gl(self, user, accounting):
        """
        Kassa operatsiyalarini accounting.services orqali yozadi — Transaction + JournalEntry + JournalLine.
        Buxgalteriya / Jurnal / Sinov balansi sahifalarida to‘liq ko‘rinish.
        """
        accounting_services.ensure_control_accounts()
        JournalLine.objects.all().delete()
        JournalEntry.objects.all().delete()
        Transaction.objects.all().delete()
        CashRegister.objects.all().update(balance=Decimal('0.00'))

        debt_reset = {
            "Toshkent Un Zavodi": Decimal("6200000.00"),
            "Sut Dunyosi MChJ": Decimal("1750000.00"),
            "Yog-Moy Savdo": Decimal("980000.00"),
        }
        for name, d in debt_reset.items():
            Supplier.objects.filter(name=name).update(debt=d)

        accounting_services.backfill_gl_for_existing_registers()

        reg = accounting["registers"]
        cat = accounting["expense_categories"]
        sup = accounting["suppliers"]

        accounting_services.record_income(
            reg["Asosiy kassa"], Decimal("18500000.00"), user, "Kunlik tushum (demo seed)"
        )
        accounting_services.record_income(
            reg["Terminal"], Decimal("7200000.00"), user, "Terminal savdo tushumi (demo)"
        )
        accounting_services.record_income(
            reg["Xarajat kassasi"], Decimal("2500000.00"), user, "Xarajat kassasi boshlang‘ich"
        )
        accounting_services.record_income(
            reg["Main Cash"], Decimal("359500.00"), user, "Kichik kassa (demo)"
        )
        accounting_services.record_income(reg["CRM"], Decimal("123.00"), user, "CRM aylanma (demo)")

        accounting_services.record_transfer(
            reg["Asosiy kassa"],
            reg["Xarajat kassasi"],
            Decimal("2000000.00"),
            user,
            "Asosiydan xarajat kassasiga ichki o‘tkazma",
        )
        accounting_services.record_expense(
            reg["Xarajat kassasi"],
            Decimal("3200000.00"),
            cat["Xomashyo"],
            user,
            "Un va xamirturush xaridi",
        )
        accounting_services.record_supplier_payment(
            reg["Asosiy kassa"],
            sup["Toshkent Un Zavodi"],
            Decimal("1500000.00"),
            user,
            "Toshkent Un Zavodiga qisman to‘lov",
        )
        accounting_services.record_supplier_debt_increase(
            sup["Yog-Moy Savdo"],
            Decimal("450000.00"),
            user,
            "Qarzga xarid: yog‘-moy partiyasi (demo)",
        )

        acc_exp = Account.objects.get(code=accounting_services.CODE_EXP)
        acc_rev = Account.objects.get(code=accounting_services.CODE_REV)
        accounting_services.post_manual_journal(
            user,
            "Namuna: qo‘lda tuzatish yozuvi (demo, teng D/K)",
            "MAN-SEED-1",
            [
                {
                    'account_id': acc_exp.id,
                    'debit': '50000.00',
                    'credit': '0',
                    'description': 'Demo qo‘lda',
                },
                {
                    'account_id': acc_rev.id,
                    'debit': '0',
                    'credit': '50000.00',
                    'description': 'Demo qo‘lda',
                },
            ],
        )

        self.stdout.write(
            self.style.NOTICE(
                "Buxgalteriya: kassa yozuvlari GL bilan yaratildi (superuser: %s)." % user.get_username()
            )
        )
