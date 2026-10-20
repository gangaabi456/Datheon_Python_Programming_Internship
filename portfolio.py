
import csv
import os
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------- Settings ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICE_FILE = os.path.join(BASE_DIR, "sp500.csv")           # download panna CSV peru
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")
W = 82                                                      # box width

SAMPLE_PRICES = {
    "AAPL": 180.00, "MSFT": 280.00, "GOOGL": 135.00, "AMZN": 125.00,
    "TSLA": 240.00, "NVDA": 450.00, "META": 300.00, "NFLX": 410.00,
    "JPM": 150.00, "KO": 58.00,
}

TICKER_COLUMNS = ["symbol", "ticker"]
PRICE_COLUMNS = ["price", "current_price", "close", "last", "adj close", "adj_close"]


# ---------- Box helpers ----------
def banner(lines):
    print("╔" + "═" * W + "╗")
    for line in lines:
        print("║" + line.center(W) + "║")
    print("╚" + "═" * W + "╝")


def box(title, lines):
    print("┌─ " + title + " " + "─" * (W - len(title) - 3) + "┐")
    for line in lines:
        print("│" + line.ljust(W) + "│")
    print("└" + "─" * W + "┘")


# ---------- Price loading (CSV) ----------
def find_column(headers, candidates):
    """CSV headers-la namma thedura column peru irukka nu paarkkum."""
    for wanted in candidates:
        for header in headers:
            if header.strip().lower() == wanted:
                return header
    return None


def load_prices(path):
    """CSV-la irundhu {ticker: price} dictionary return pannum."""
    prices = {}
    try:
        with open(path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            ticker_col = find_column(reader.fieldnames or [], TICKER_COLUMNS)
            price_col = find_column(reader.fieldnames or [], PRICE_COLUMNS)

            if ticker_col is None or price_col is None:
                return SAMPLE_PRICES, "SAMPLE prices (CSV-la symbol/price column kidaikkala)"

            for row in reader:
                try:
                    price = float(str(row[price_col]).replace(",", ""))
                except (ValueError, TypeError):
                    continue  # price illatha row-a skip
                prices[row[ticker_col].strip().upper()] = price

    except FileNotFoundError:
        return SAMPLE_PRICES, "SAMPLE prices (sp500.csv kidaikkala)"

    if not prices:
        return SAMPLE_PRICES, "SAMPLE prices (CSV-la valid prices illa)"
    return prices, "sp500.csv (" + str(len(prices)) + " tickers)"


# ---------- Input helpers ----------
def ask_ticker(prices):
    while True:
        ticker = input("  Ticker symbol (e.g. AAPL): ").strip().upper()
        if ticker in prices:
            return ticker
        print("  ✘ '" + ticker + "' CSV-la illa. Vera ticker try pannunga.")


def ask_number(prompt, number_type):
    """Positive number mattum accept pannum. Letters / 0 / negative = thirumba keppom."""
    while True:
        text = input(prompt).strip()
        try:
            value = number_type(text)
        except ValueError:
            print("  ✘ Number mattum type pannunga.")
            continue
        if value <= 0:
            print("  ✘ 0-ku mela irukkanum.")
            continue
        return value


# ---------- Portfolio logic ----------
def add_stock(portfolio, prices):
    print()
    ticker = ask_ticker(prices)
    buy_price = ask_number("  Buy price per share: ", float)
    shares = ask_number("  Number of shares: ", int)

    if ticker in portfolio:
        old = portfolio[ticker]
        total_shares = old["shares"] + shares
        total_cost = old["buy_price"] * old["shares"] + buy_price * shares
        portfolio[ticker] = {"buy_price": total_cost / total_shares, "shares": total_shares}
        print("  ✔ " + ticker + " updated (average buy price kanakku pannitten).")
    else:
        portfolio[ticker] = {"buy_price": buy_price, "shares": shares}
        print("  ✔ " + ticker + " added.")


def remove_stock(portfolio):
    if not portfolio:
        print("\n  ⚠ Portfolio kaali, remove panna onnum illa.")
        return
    ticker = input("\n  Remove which ticker? ").strip().upper()
    if ticker in portfolio:
        del portfolio[ticker]
        print("  ✔ " + ticker + " removed.")
    else:
        print("  ✘ '" + ticker + "' portfolio-la illa.")


def calculate(portfolio, prices):
    """Ovvoru stock-kum invested, value, gain, % kanakku pannum."""
    holdings = []
    for ticker, data in portfolio.items():
        current = prices[ticker]
        invested = data["buy_price"] * data["shares"]
        value = current * data["shares"]
        gain = value - invested
        pct = (current - data["buy_price"]) / data["buy_price"] * 100
        holdings.append({
            "ticker": ticker,
            "shares": data["shares"],
            "buy_price": data["buy_price"],
            "current": current,
            "invested": invested,
            "value": value,
            "gain": gain,
            "pct": pct,
        })

    total_invested = sum(h["invested"] for h in holdings)
    total_value = sum(h["value"] for h in holdings)
    total_gain = total_value - total_invested
    total_pct = total_gain / total_invested * 100 if total_invested else 0
    totals = {"invested": total_invested, "value": total_value,
              "gain": total_gain, "pct": total_pct}
    return holdings, totals


# ---------- Display ----------
def arrow(number):
    return "▲" if number >= 0 else "▼"


def show_table(holdings):
    print("  " + "Ticker".ljust(7) + " " + "Shares".rjust(6) + " " + "Buy".rjust(9) + " "
          + "Now".rjust(9) + " " + "Invested".rjust(11) + " " + "Value".rjust(11) + " "
          + "Gain/Loss".rjust(11) + " " + "%".rjust(9))
    print("  " + "─" * (W - 2))
    for h in holdings:
        print(arrow(h["gain"]) + " "
              + h["ticker"].ljust(7) + " "
              + str(h["shares"]).rjust(6) + " "
              + f"{h['buy_price']:>9,.2f} "
              + f"{h['current']:>9,.2f} "
              + f"{h['invested']:>11,.2f} "
              + f"{h['value']:>11,.2f} "
              + f"{h['gain']:>+11,.2f} "
              + f"{h['pct']:>+8.2f}%")
    print("  " + "─" * (W - 2))


def show_bars(holdings):
    """Ovvoru stock-oda % ku oru bar (1 block = 2%, max 30)."""
    lines = []
    for h in holdings:
        length = min(int(abs(h["pct"]) / 2), 30)
        bar = "█" * length if length > 0 else "▏"
        lines.append("  " + h["ticker"].ljust(7) + arrow(h["pct"]) + " " + bar
                     + f" {h['pct']:+.2f}%")
    box("PERFORMANCE (1 block = 2%)", lines)


def show_totals(totals, holdings):
    best = max(holdings, key=lambda h: h["pct"])
    worst = min(holdings, key=lambda h: h["pct"])
    box("SUMMARY", [
        "",
        f"   Total Invested : {totals['invested']:>14,.2f}",
        f"   Current Value  : {totals['value']:>14,.2f}",
        f"   Net Gain/Loss  : {totals['gain']:>+14,.2f}  ({arrow(totals['gain'])} {totals['pct']:+.2f}%)",
        "",
        f"   Best performer  : {best['ticker']}  ({best['pct']:+.2f}%)",
        f"   Worst performer : {worst['ticker']}  ({worst['pct']:+.2f}%)",
        "",
    ])


def view_portfolio(portfolio, prices):
    if not portfolio:
        print("\n  ⚠ Portfolio kaali. Mudhalla oru stock add pannunga (option 1).")
        return None, None
    holdings, totals = calculate(portfolio, prices)
    print()
    show_table(holdings)
    print()
    show_bars(holdings)
    show_totals(totals, holdings)
    return holdings, totals


# ---------- CSV saving ----------
def save_summary(holdings, totals, path):
    """portfolio_summary.csv-la ellaa results-um eludhum."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "ticker", "shares", "buy_price", "current_price",
                         "invested", "current_value", "gain_loss", "gain_loss_pct"])
        for h in holdings:
            writer.writerow([stamp, h["ticker"], h["shares"],
                             round(h["buy_price"], 2), round(h["current"], 2),
                             round(h["invested"], 2), round(h["value"], 2),
                             round(h["gain"], 2), round(h["pct"], 2)])
        writer.writerow([stamp, "TOTAL", "", "", "",
                         round(totals["invested"], 2), round(totals["value"], 2),
                         round(totals["gain"], 2), round(totals["pct"], 2)])


# ---------- Main program ----------
def show_menu():
    print()
    box("MENU", [
        "   [1]  Add a stock",
        "   [2]  View portfolio",
        "   [3]  Remove a stock",
        "   [4]  Save summary & exit",
    ])


def main():
    prices, source = load_prices(PRICE_FILE)
    portfolio = {}

    print()
    banner(["", "S T O C K   P O R T F O L I O   T R A C K E R", "",
            "Prices from: " + source, ""])

    while True:
        show_menu()
        choice = input("  ➤ Choose (1-4): ").strip()

        if choice == "1":
            add_stock(portfolio, prices)
        elif choice == "2":
            view_portfolio(portfolio, prices)
        elif choice == "3":
            remove_stock(portfolio)
        elif choice == "4":
            holdings, totals = view_portfolio(portfolio, prices)
            if holdings:
                save_summary(holdings, totals, SUMMARY_FILE)
                print("\n  ✔ Summary saved to " + os.path.basename(SUMMARY_FILE))
            print("\n  Thanks for using the tracker! 👋\n")
            break
        else:
            print("\n  ⚠ 1 mudhal 4 varaikum mattum type pannunga.")


if __name__ == "__main__":
    main()