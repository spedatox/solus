# Using Solus: a small accounting walkthrough

A **book** is an independent set of records, such as Personal or Freelance. An **account** is a named bucket: Bank is an asset, Credit card is a liability, Food is an expense, Salary is income, and Opening equity explains starting balances. Accounts include categories as well as places that hold money.

A **journal event** records one financial occurrence through balanced debit/credit lines. Debit increases assets and expenses. Credit increases liabilities, income and equity; the opposite side decreases them. A debit is not always what you bought, and a credit is not always the place you paid from.

Suppose you buy 600 TRY of food using a card. Debit Food 600 and credit Card 600: expense increases and card debt increases. Later pay the card from your bank: debit Card 600 and credit Bank 600. That reduces debt and bank cash; it does not create another food expense.

For a three-installment 1000 TRY purchase, the journal records the purchase once. Solus creates obligations of 333.34, 333.33 and 333.33 TRY. Configure the card closing date and due-date rule before posting; a purchase booked after closing moves to the next statement. If the bank prints different actual dates, enter that statement's override.

| Menu | Purpose |
| --- | --- |
| Overview | Select/create a book and inspect monthly native-currency totals. |
| Accounts | Create the five kinds of account and choose their currency. |
| Journal | Record actual occurrences; use the relevant operation and balanced lines. Inspect and reverse mistakes. |
| Cards & statements | Configure calendars, enter printed statement dates/balances and inspect billed obligations. |
| Obligations | Inspect unpaid installments, invoices, bills and their due dates; settlements are recorded through the journal. |
| Plans | Record budgets, recurring estimates and goals. These are planning records, not actual expenses. |
| Investments | Record purchases/disposals and separate cost basis from observed market value. |
| Reports | Read exact business balances, aging, holdings and reconciliation results. |
| Import & history | Preview mapped CSV transactions before atomic import. Journal history remains in Journal. |
| Period controls | Close reviewed historical periods to reject late postings. |
| Settings | Change your password and sign out. |

Begin with one book, a bank asset account, an opening-equity account, expense categories, income categories and any card liability accounts. Record opening balances with the Opening operation; configure cards next; then record actual transactions. Reconcile with real bank/card statements before closing a period. Never import the same purchase again as both an expense and its later card payment.
