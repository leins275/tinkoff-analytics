import os

from datetime import datetime
from dotenv import load_dotenv
from tinkoff.invest import Client, GetOperationsByCursorRequest, OperationType
from pprint import pprint
from loguru import logger


load_dotenv()
token = os.environ["TINKOFF_TOKEN"]

OP_PAY_IN = OperationType(1) # Пополнение брокерского счета
OP_OUT    = OperationType(9) # Вывод денежных средств

class TinAnal:
    def __init__(self) -> None:
        self.actual_account_names = ["ETF", "Долгосрочный инвестор - Россия", "Bonds", "Копилка"]
        self.account_ids = self._get_accounts()

    def _get_accounts(self) -> list:
        with Client(token) as client:
            accounts = client.users.get_accounts().accounts
            actual_accounts = [acc for acc in accounts if acc.name in self.actual_account_names]
            logger.info(f"My actual accounts:")
            # pprint(actual_accounts)
            return [acc.id for acc in actual_accounts]
    
    def get_account_pay_in(self, account_id, start, end):
        with Client(token) as client:
            req = GetOperationsByCursorRequest(
                    account_id=account_id,
                    operation_types=[OP_PAY_IN], 
                    from_=start, 
                    to=end
                    )
            operations = client.operations.get_operations_by_cursor(req)

            sum = 0
            for op in operations.items:
                sum += op.payment.units

            return sum

    def _get_operations(self, account_id, start, end):
        start = datetime.strptime(start, "%Y-%m-%d")
        end   = datetime.strptime(end, "%Y-%m-%d")
        with Client(token) as client:
            req = GetOperationsByCursorRequest(
                    account_id=account_id,
                    from_=start, 
                    to=end
                    )
            operations = client.operations.get_operations_by_cursor(req)

            logger.info("operations:")
            pprint([(op_it.type, op_it.description, op_it.date) for op_it in operations.items])
            sum = 0
            for op in operations.items:
                sum += op.payment.units

            return sum

    def get_sum_pay_in(self, start, end):
        all_acc_pay_in = 0
        for account_id in self.account_ids:
            all_acc_pay_in += self.get_account_pay_in(account_id, start, end)

        return all_acc_pay_in


    def get_portfolio_sum(self):
        total_sum = 0
        with Client(token) as client:
            for account_id in self.account_ids:
                portfolio = client.operations.get_portfolio(account_id=account_id)
                total_sum += portfolio.total_amount_portfolio.units
        return total_sum


    def analyze(self, start_date="", end_date=""):
        start_date_timestamp = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_timestamp   = datetime.strptime(end_date, "%Y-%m-%d")

        portfolio_sum = self.get_portfolio_sum()
        sum_pay_in    = self.get_sum_pay_in(start_date_timestamp, end_date_timestamp)

        # profit_in_rub     = portfolio_sum - sum_pay_in
        # profit_in_percent = 100 * round(profit_in_rub / sum_pay_in, 4)

        print(f"За период {start_date} - {end_date}:\n-------------------------\n"
              f"Пополнения: {sum_pay_in:n} руб\n"
              f"Текущая  рублёвая стоимость портфеля: {portfolio_sum:n} руб\n")


if __name__ ==  "__main__":
    analytics = TinAnal()

    # analytics._get_operations(analytics.account_ids[3], "2024-06-05", "2024-06-08")
    analytics.analyze("2024-05-01", "2024-05-31")
