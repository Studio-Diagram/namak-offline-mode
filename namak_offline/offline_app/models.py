from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=4 * 255, null=False, blank=False)
    start_working_time = models.TimeField(null=True)
    end_working_time = models.TimeField(null=True)


class Employee(models.Model):
    phone = models.CharField(max_length=30, null=False, blank=False)
    password = models.TextField(null=False, blank=False)


class TableCategory(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return str(self.name)


class Table(models.Model):
    name = models.CharField(max_length=255, null=False)
    category = models.ForeignKey(to=TableCategory, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class Cash(models.Model):
    created_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ended_date_time = models.DateTimeField(null=True, blank=True)
    income_report = models.IntegerField(null=False, default=0)
    outcome_report = models.IntegerField(null=False, default=0)
    event_tickets = models.IntegerField(null=False, default=0)
    current_money_in_cash = models.IntegerField(null=False, default=0)
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE)
    branch = models.ForeignKey(to=Branch, on_delete=models.CASCADE)
    is_close = models.SmallIntegerField(default=0, null=False)


class Printer(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)


class MenuCategory(models.Model):
    KIND = (
        ('KITCHEN', 'آشپزخانه'),
        ('BAR', 'بار'),
        ('OTHER', 'سایر'),
    )
    name = models.CharField(max_length=30, null=True, blank=True)
    kind = models.CharField(max_length=50, choices=KIND, blank=False, null=False)
    list_order = models.IntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.name


class PrinterToCategory(models.Model):
    printer = models.ForeignKey(Printer, null=True, blank=False, on_delete=models.CASCADE)
    menu_category = models.ForeignKey(MenuCategory, null=True, blank=False, on_delete=models.CASCADE)


class MenuItem(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    price = models.CharField(max_length=30, null=True, blank=True)
    is_delete = models.SmallIntegerField(default=0, null=False)
    menu_category = models.ForeignKey(MenuCategory, null=True, blank=False, on_delete=models.CASCADE)


class Member(models.Model):
    last_name = models.CharField(max_length=255, null=False)
    card_number = models.CharField(max_length=20, null=False, unique=True)
    server_primary_key = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.last_name


class Game(models.Model):
    member = models.ForeignKey(to=Member, on_delete=models.CASCADE)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=True, default="00:00:00")
    numbers = models.IntegerField(null=False)
    points = models.IntegerField(null=False, default=0)
    add_date = models.DateField(null=False)

    def __str__(self):
        return str(self.member.last_name + " " + str(self.start_time))


class InvoiceSales(models.Model):
    SETTLEMENT_CHOICES = (
        ('BANK_CARD', 'کارت بانکی'),
        ('CASH', 'نقدی'),
    )
    GAME_STATES = (
        ('NO_GAME', 'بازی نمی‌خواهد'),
        ('PLAYING', 'در حال بازی'),
        ('WAIT_GAME', 'منتظر بازی'),
        ('END_GAME', 'بازی تمام شده'),
    )
    factor_number = models.IntegerField(null=False, blank=False, default=0)
    created_time = models.DateTimeField(null=False)
    settle_time = models.DateTimeField(null=True, blank=True)
    cash = models.FloatField(null=False, default=0)
    pos = models.FloatField(null=False, default=0)
    discount = models.FloatField(null=False, default=0)
    employee_discount = models.FloatField(null=False, default=0)
    tax = models.FloatField(null=False, default=0)
    tip = models.FloatField(null=False, default=0)
    settlement_type = models.CharField(max_length=50, choices=SETTLEMENT_CHOICES, default='CASH')
    guest_numbers = models.IntegerField(null=False)
    is_settled = models.IntegerField(null=False, default=0)
    total_price = models.FloatField(default=0)
    member = models.ForeignKey(to=Member, on_delete=models.CASCADE, default=0)
    table = models.ForeignKey(to=Table, on_delete=models.CASCADE)
    ready_for_settle = models.BooleanField(default=False)
    cash_desk = models.ForeignKey(Cash, null=True, blank=True, on_delete=models.CASCADE)
    branch = models.ForeignKey(to=Branch, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    is_do_not_want_order = models.BooleanField(default=False)
    game_state = models.CharField(max_length=50, choices=GAME_STATES, default='WAIT_GAME')

    def __str__(self):
        return "num: " + str(self.factor_number) + " total_p: " + str(self.total_price) + " Is Settled: " + str(
            self.is_settled) + " member: " + self.member.last_name


class InvoicesSalesToMenuItem(models.Model):
    invoice_sales = models.ForeignKey(to=InvoiceSales, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(to=MenuItem, on_delete=models.CASCADE)
    numbers = models.IntegerField(null=False)
    description = models.CharField(max_length=60, blank=True)
    is_print = models.SmallIntegerField(default=0, null=False)


class InvoicesSalesToGame(models.Model):
    invoice_sales = models.ForeignKey(to=InvoiceSales, on_delete=models.CASCADE)
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE)


class Reservation(models.Model):
    STATES = (
        ('waiting', 'waiting'),
        ('arrived', 'arrived'),
        ('walked', 'walked'),
        ('call_waiting', 'call_waiting'),
    )
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    numbers = models.IntegerField(null=False)
    reserve_date = models.DateTimeField(null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    reserve_state = models.CharField(max_length=50, choices=STATES)
    branch = models.ForeignKey(to=Branch, on_delete=models.CASCADE, null=True)


class ReserveToTables(models.Model):
    reserve = models.ForeignKey(to=Reservation, on_delete=models.CASCADE)
    table = models.ForeignKey(to=Table, on_delete=models.CASCADE)


class SavedUsedAPIs(models.Model):
    METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('DELETE', 'DELETE'),
        ('PUT', 'PUT'),
    )
    api_url = models.CharField(max_length=2550, null=False, blank=False)
    api_method = models.CharField(max_length=2550, choices=METHODS, default='GET')
    payload = models.TextField(default="")