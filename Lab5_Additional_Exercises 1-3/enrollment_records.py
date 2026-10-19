"""University Enrollment Records - consolidating two sorted department lists.

Usage:
    python enrollment_merge.py
    python enrollment_merge.py Bernal TUPM-26-1940 BTS
"""
import sys


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
        "LAST_NAME": last.strip(),
        "STUDENT_ID": sid.strip(),
        "FAVORITE_ARTIST": artist.strip(),
        "SEED_DIGIT": digits[-1],
        "ID_SUM": sum(digits),
        "NAME_LENGTH": len(last.strip()),
        "ARTIST_LENGTH": len(letters),
        "ARTIST_SUM": sum(ord(c) - 64 for c in letters),
    }


# ---------------------------------------------------------------------------
# 1. Generate the two sorted datasets
# ---------------------------------------------------------------------------
def generate_a(v):
    """Dataset A (uses SEED_DIGIT and ID_SUM).
    count = ID_SUM, first = 1000 + SEED_DIGIT, step = (ID_SUM mod 10) + 1."""
    step = v["ID_SUM"] % 10 + 1
    return [1000 + v["SEED_DIGIT"] + step * i for i in range(v["ID_SUM"])]


def generate_b(v):
    """Dataset B (uses ARTIST_LENGTH and NAME_LENGTH).
    count = NAME_LENGTH + ARTIST_LENGTH, first = 1000 + ARTIST_LENGTH,
    step = NAME_LENGTH + 1."""
    count = v["NAME_LENGTH"] + v["ARTIST_LENGTH"]
    step = v["NAME_LENGTH"] + 1
    return [1000 + v["ARTIST_LENGTH"] + step * i for i in range(count)]


# ---------------------------------------------------------------------------
# 2-3. Consolidate (two-pointer merge) and count comparisons
#      One comparison = one test of a[i] <= b[j]. Copying leftover records
#      after one list runs out needs no comparisons.
# ---------------------------------------------------------------------------
def merge(a, b):
    i = j = comparisons = 0
    merged, source = [], []
    while i < len(a) and j < len(b):
        comparisons += 1
        if a[i] <= b[j]:          # ties take A first, so the merge is stable
            merged.append(a[i]); source.append("A"); i += 1
        else:
            merged.append(b[j]); source.append("B"); j += 1
    while i < len(a):
        merged.append(a[i]); source.append("A"); i += 1
    while j < len(b):
        merged.append(b[j]); source.append("B"); j += 1
    return merged, source, comparisons


# ---------------------------------------------------------------------------
# 4. Verification
# ---------------------------------------------------------------------------
def verify(a, b, merged):
    return {
        "Ascending order": all(merged[k] <= merged[k + 1] for k in range(len(merged) - 1)),
        "Record count (A + B = merged)": len(merged) == len(a) + len(b),
        "Same records as A + B": sorted(a + b) == merged,
    }


def main():
    v = derive(*get_inputs())
    a, b = generate_a(v), generate_b(v)
    merged, source, comps = merge(a, b)
    n, m = len(a), len(b)
    dups = sorted(set(a) & set(b))
    checks = verify(a, b, merged)

    bar, dash, out = "=" * 74, "-" * 74, []
    P = out.append
    P(bar)
    P("UNIVERSITY ENROLLMENT RECORDS - CONSOLIDATION REPORT")
    P(bar)
    P("STUDENT-SPECIFIC VALUES")
    P(dash)
    for key in ("LAST_NAME", "STUDENT_ID", "FAVORITE_ARTIST", "SEED_DIGIT", "ID_SUM",
                "NAME_LENGTH", "ARTIST_LENGTH", "ARTIST_SUM"):
        P(f"{key:<17}: {v[key]}")

    P("")
    P("1. DEPARTMENT A DATASET")
    P(dash)
    P(f"Rule: {n} records (ID_SUM), first = 1000 + SEED_DIGIT, step = (ID_SUM mod 10) + 1")
    P(str(a))
    P("")
    P("2. DEPARTMENT B DATASET")
    P(dash)
    P(f"Rule: {m} records (NAME_LENGTH + ARTIST_LENGTH), first = 1000 + ARTIST_LENGTH, "
      f"step = NAME_LENGTH + 1")
    P(str(b))

    P("")
    P("3. CONSOLIDATED DATASET (source department in brackets)")
    P(dash)
    P(", ".join(f"{x}[{s}]" for x, s in zip(merged, source)))
    P(f"Student IDs in both departments (kept as separate records): {dups if dups else 'none'}")

    P("")
    P("4. NUMBER OF RECORDS")
    P(dash)
    P(f"Before consolidation : A = {n}, B = {m}, total = {n + m}")
    P(f"After consolidation  : {len(merged)}")

    P("")
    P("5. COMPARISON COUNT")
    P(dash)
    P(f"Comparisons performed: {comps}")
    P(f"Best case  (one list is entirely smaller): min(n, m) = {min(n, m)}")
    P(f"Worst case (records alternate)           : n + m - 1 = {n + m - 1}")

    P("")
    P("6. ORDERING VERIFICATION")
    P(dash)
    for name, ok in checks.items():
        P(f"{name:<32}: {'PASS' if ok else 'FAIL'}")

    P("")
    P("7. TIME AND SPACE COMPLEXITY")
    P(dash)
    P(f"Time : O(n + m) - each record is placed once; at most n + m - 1 = {n + m - 1} comparisons")
    P("Space: O(n + m) - a new list holds all merged records (the inputs are not modified)")
    P("       (the extra working variables are O(1))")

    P("")
    P("FINAL OUTPUT")
    P(dash)
    P(f"Final consolidated enrollment list ({len(merged)} records): {merged}")
    P(bar)

    report = "\n".join(out)
    print(report)
    with open("enrollment_merge_report.txt", "w") as f:
        f.write(report)


if __name__ == "__main__":
    main()