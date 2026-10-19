"""E-Commerce Order Processing - Bubble vs Selection vs Insertion Sort.

Usage:
    python order_sorting.py
    python order_sorting.py Bernal TUPM-26-1940 BTS
"""
import random
import sys
import time

REPEATS = 2000  # each sort is timed this many times and averaged (the lists are tiny)


# ---------------------------------------------------------------------------
# Student-specific values
# ---------------------------------------------------------------------------
def get_inputs():
    if len(sys.argv) == 4:
        return sys.argv[1], sys.argv[2], sys.argv[3]
    return (input("LAST_NAME: "), input("STUDENT_ID: "), input("FAVORITE_ARTIST: "))


def derive(last, sid, artist):
    digits = [int(c) for c in sid if c.isdigit()]
    letters = [c for c in artist.upper() if c.isalpha()]
    return {
        "LAST_NAME": last.strip(), "STUDENT_ID": sid.strip(),
        "FAVORITE_ARTIST": artist.strip(),
        "SEED_DIGIT": digits[-1], "ID_SUM": sum(digits),
        "NAME_LENGTH": len(last.strip()), "ARTIST_LENGTH": len(letters),
        "ARTIST_SUM": sum(ord(c) - 64 for c in letters),
    }


# ---------------------------------------------------------------------------
# 1. Generate the orders and the three input conditions (same orders each time)
# ---------------------------------------------------------------------------
def generate_orders(v):
    """count = ID_SUM order numbers, first = 1000 + ARTIST_SUM, step = NAME_LENGTH."""
    return [1000 + v["ARTIST_SUM"] + v["NAME_LENGTH"] * i for i in range(v["ID_SUM"])]


def make_conditions(orders, v):
    rng = random.Random(v["ID_SUM"] * v["ARTIST_SUM"])      # reproducible shuffle
    shuffled = orders[:]
    while len(orders) > 1 and shuffled == orders:
        rng.shuffle(shuffled)
    return {"Sorted": orders[:], "Reverse": orders[::-1], "Random": shuffled}


# ---------------------------------------------------------------------------
# 2-3. Sorting algorithms.  Each returns (sorted_list, comparisons, movements).
#      Comparison = one comparison between two order numbers.
#      Movement   = one write of an order into the list (a swap = 2 movements).
# ---------------------------------------------------------------------------
def bubble_sort(data):
    a, cmp, mov, n = data[:], 0, 0, len(data)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            cmp += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                mov += 2
                swapped = True
        if not swapped:            # early exit: already sorted
            break
    return a, cmp, mov


def selection_sort(data):
    a, cmp, mov, n = data[:], 0, 0, len(data)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            cmp += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            mov += 2
    return a, cmp, mov


def insertion_sort(data):
    a, cmp, mov = data[:], 0, 0
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0:
            cmp += 1
            if a[j] > key:
                a[j + 1] = a[j]    # shift right
                mov += 1
                j -= 1
            else:
                break
        if j + 1 != i:
            a[j + 1] = key         # place the key
            mov += 1
    return a, cmp, mov


ALGORITHMS = {"Bubble Sort": bubble_sort, "Selection Sort": selection_sort,
              "Insertion Sort": insertion_sort}


def time_sort(fn, data):
    """Average execution time in microseconds over REPEATS runs."""
    start = time.perf_counter_ns()
    for _ in range(REPEATS):
        fn(data)
    return (time.perf_counter_ns() - start) / REPEATS / 1000


def run_all(conditions):
    results = {}
    for algo, fn in ALGORITHMS.items():
        for cond, data in conditions.items():
            out, cmp, mov = fn(data)
            results[(algo, cond)] = {"cmp": cmp, "mov": mov, "time": time_sort(fn, data),
                                     "ok": out == sorted(data)}
    return results


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def table(title, results, key, fmt, conds, out):
    if title:
        out.append(title)
    out.append(f"{'Algorithm':<18}" + "".join(f"{c:>12}" for c in conds))
    for algo in ALGORITHMS:
        out.append(f"{algo:<18}" + "".join(f"{fmt(results[(algo, c)][key]):>12}" for c in conds))


def main():
    v = derive(*get_inputs())
    orders = generate_orders(v)
    conditions = make_conditions(orders, v)
    conds = list(conditions)
    n = len(orders)
    results = run_all(conditions)

    bar, dash, out = "=" * 74, "-" * 74, []
    P = out.append
    P(bar)
    P("E-COMMERCE ORDER PROCESSING - SORTING PERFORMANCE REPORT")
    P(bar)
    P("STUDENT-SPECIFIC VALUES")
    P(dash)
    for key in ("LAST_NAME", "STUDENT_ID", "FAVORITE_ARTIST", "SEED_DIGIT", "ID_SUM",
                "NAME_LENGTH", "ARTIST_LENGTH", "ARTIST_SUM"):
        P(f"{key:<17}: {v[key]}")

    P("")
    P("1. GENERATED ORDER DATASET")
    P(dash)
    P(f"Rule: {n} orders (ID_SUM), first = 1000 + ARTIST_SUM, step = NAME_LENGTH")
    P(str(orders))

    P("")
    P("2. SORTED, REVERSE, AND RANDOM INPUTS (same orders, different arrangement)")
    P(dash)
    for c in conds:
        P(f"{c + ':':<9}{conditions[c]}")
    P(f"(Random uses a fixed shuffle seed = ID_SUM x ARTIST_SUM = {v['ID_SUM'] * v['ARTIST_SUM']}, "
      f"so results are repeatable.)")

    P("")
    P("3. COMPARISON COUNTS")
    P(dash)
    table("", results, "cmp", str, conds, out)
    P("")
    P("4. MOVEMENT COUNTS (a swap = 2 movements, a shift or placement = 1)")
    P(dash)
    table("", results, "mov", str, conds, out)
    P("")
    P(f"5. EXECUTION TIMES (microseconds, average of {REPEATS} runs)")
    P(dash)
    table("", results, "time", lambda t: f"{t:.2f}", conds, out)

    P("")
    P("6. SORTING VERIFICATION")
    P(dash)
    P(f"{'Algorithm':<18}" + "".join(f"{c:>12}" for c in conds))
    for algo in ALGORITHMS:
        P(f"{algo:<18}" + "".join(f"{'PASS' if results[(algo, c)]['ok'] else 'FAIL':>12}" for c in conds))
    P(f"All {len(results)} runs match Python's sorted(): "
      f"{'YES' if all(r['ok'] for r in results.values()) else 'NO'}")

    full = n * (n - 1) // 2
    P("")
    P("7. BIG O ANALYSIS")
    P(dash)
    P(f"{'Algorithm':<18}{'Best':<9}{'Average':<10}{'Worst':<9}{'Space':<7}{'Stable'}")
    P(f"{'Bubble Sort':<18}{'O(n)':<9}{'O(n^2)':<10}{'O(n^2)':<9}{'O(1)':<7}Yes")
    P(f"{'Selection Sort':<18}{'O(n^2)':<9}{'O(n^2)':<10}{'O(n^2)':<9}{'O(1)':<7}No")
    P(f"{'Insertion Sort':<18}{'O(n)':<9}{'O(n^2)':<10}{'O(n^2)':<9}{'O(1)':<7}Yes")
    P(f"(Bubble Sort uses an early exit when a pass makes no swaps, which gives its O(n) best case.)")
    P(f"For n = {n}: n-1 = {n - 1} comparisons (linear), n(n-1)/2 = {full} comparisons (quadratic).")

    P("")
    P("8. BEST-, AVERAGE-, AND WORST-CASE OBSERVATIONS")
    P(dash)
    P(f"Best case  = Sorted input, Worst case = Reverse input, Average case = Random input.")
    for algo in ALGORITHMS:
        c = {k: results[(algo, k)] for k in conds}
        P(f"{algo}: comparisons {c['Sorted']['cmp']} (best) / {c['Random']['cmp']} (average) / "
          f"{c['Reverse']['cmp']} (worst); movements {c['Sorted']['mov']} / "
          f"{c['Random']['mov']} / {c['Reverse']['mov']}")
    P("")
    for cond in conds:
        def best(key):
            low = min(results[(a, cond)][key] for a in ALGORITHMS)
            return " & ".join(a for a in ALGORITHMS if results[(a, cond)][key] == low)
        P(f"{cond + ' input:':<15}fewest comparisons = {best('cmp')}; "
          f"fewest movements = {best('mov')}; fastest = {best('time')}")
    P("")
    P("Observations:")
    P(f"- Selection Sort makes {full} comparisons on every input, so its comparison count does not")
    P("  depend on the order. It makes the fewest movements overall (at most one swap per pass).")
    P("- Bubble and Insertion Sort adapt to the input: on sorted data they need only n-1 comparisons")
    P("  and no movements, but on reverse data they reach the quadratic worst case.")
    P("- Random input falls between the two extremes, matching the O(n^2) average case.")
    P("- Execution times follow the comparison and movement counts, but they vary with the machine")
    P("  and include the cost of the counters; the counts are the more reliable measure.")

    P("")
    P("FINAL OUTPUT")
    P(dash)
    P(f"{n} orders sorted by 3 algorithms under 3 input conditions: all 9 results verified sorted.")
    P(bar)

    report = "\n".join(out)
    print(report)
    with open("order_sorting_report.txt", "w") as f:
        f.write(report)


if __name__ == "__main__":
    main()