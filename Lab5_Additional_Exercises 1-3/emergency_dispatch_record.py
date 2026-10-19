"""Emergency Dispatch Record Search
Rotated sorted list search (modified binary search) vs. Linear Search.

Usage:
    python dispatch_search.py
    python dispatch_search.py Bernal TUPM-26-1940 BTS
"""
import math
import sys

# If you want a rotation even when SEED_DIGIT is 0, set this to a number (e.g. 5).
ROTATION_OVERRIDE = None


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
        "SEED_DIGIT": digits[-1],                               # last digit of STUDENT_ID
        "ID_SUM": sum(digits),                                  # sum of STUDENT_ID digits
        "NAME_LENGTH": len(last.strip()),                       # length of LAST_NAME
        "ARTIST_LENGTH": len(letters),                          # length of FAVORITE_ARTIST
        "ARTIST_SUM": sum(ord(c) - 64 for c in letters),        # A=1 ... Z=26
    }


# ---------------------------------------------------------------------------
# 1. Generate the original and rotated incident records
# ---------------------------------------------------------------------------
def generate_records(v):
    """Unique, ascending incident numbers built from the student-specific values.

    count = ID_SUM records, starting at 1000 + ARTIST_SUM, spaced NAME_LENGTH apart.
    """
    n = v["ID_SUM"]
    start = 1000 + v["ARTIST_SUM"]
    step = v["NAME_LENGTH"]
    return [start + step * i for i in range(n)]


def rotate(records, k):
    """Move the first k records to the end of the list."""
    k %= len(records)
    return records[k:] + records[:k]


def make_target(records, v):
    """Target incident chosen using ID_SUM and ARTIST_SUM (always a real record)."""
    return records[(v["ID_SUM"] + v["ARTIST_SUM"]) % len(records)]


# ---------------------------------------------------------------------------
# 2-4. Searches (each returns index or -1, comparison count, and a trace)
#      "Comparisons" = records examined against the target (one per probe).
#      The rotated binary search also makes extra internal range checks to decide
#      which half to keep; these are reported separately as "total checks".
# ---------------------------------------------------------------------------
def rotated_binary_search(arr, target):
    lo, hi, cmp, probes, trace = 0, len(arr) - 1, 0, 0, []
    while lo <= hi:
        mid = (lo + hi) // 2
        trace.append((lo, hi, mid, arr[mid]))
        probes += 1
        cmp += 1                                  # arr[mid] == target
        if arr[mid] == target:
            return mid, probes, cmp, trace
        cmp += 1                                  # arr[lo] <= arr[mid]  (left half sorted?)
        if arr[lo] <= arr[mid]:
            cmp += 1                              # arr[lo] <= target
            if arr[lo] <= target:
                cmp += 1                          # target < arr[mid]
                if target < arr[mid]:
                    hi = mid - 1
                else:
                    lo = mid + 1
            else:
                lo = mid + 1
        else:
            cmp += 1                              # target <= arr[hi]
            if target <= arr[hi]:
                cmp += 1                          # target > arr[mid]
                if target > arr[mid]:
                    lo = mid + 1
                else:
                    hi = mid - 1
            else:
                hi = mid - 1
    return -1, probes, cmp, trace


def linear_search(arr, target):
    cmp = 0
    for i, x in enumerate(arr):
        cmp += 1                                  # x == target
        if x == target:
            return i, cmp
    return -1, cmp


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def describe(idx):
    return f"FOUND at index {idx} (position {idx + 1})" if idx >= 0 else "NOT FOUND"


def main():
    v = derive(*get_inputs())
    k = ROTATION_OVERRIDE if ROTATION_OVERRIDE is not None else v["SEED_DIGIT"]

    original = generate_records(v)
    rotated = rotate(original, k)
    target = make_target(original, v)
    missing = original[-1] + 1                     # guaranteed-absent value (not-found demo)
    n = len(original)

    bar, dash, out = "=" * 74, "-" * 74, []
    P = out.append
    P(bar)
    P("EMERGENCY DISPATCH RECORD SEARCH REPORT")
    P(bar)
    P("STUDENT-SPECIFIC VALUES")
    P(dash)
    for key in ("LAST_NAME", "STUDENT_ID", "FAVORITE_ARTIST", "SEED_DIGIT", "ID_SUM",
                "NAME_LENGTH", "ARTIST_LENGTH", "ARTIST_SUM"):
        P(f"{key:<17}: {v[key]}")
    P(f"{'RECORD COUNT':<17}: {n}  (= ID_SUM)")
    P(f"{'ROTATION POINT':<17}: {k % n}  (first {k % n} record(s) moved to the end)")
    if k % n == 0:
        P("  Note: rotation point 0 means the list is not rotated; the search still works.")

    P("")
    P("1. ORIGINAL DATASET (sorted)")
    P(dash)
    P(str(original))
    P("")
    P("2. ROTATED DATASET")
    P(dash)
    P(str(rotated))

    P("")
    P("3. TARGET INCIDENT")
    P(dash)
    P(f"Target = record #{(v['ID_SUM'] + v['ARTIST_SUM']) % n} of the original list "
      f"(index = (ID_SUM + ARTIST_SUM) mod {n}) -> {target}")

    for label, tgt in (("SEARCH RESULTS - target incident", target),
                       ("SEARCH RESULTS - missing incident (not-found demo)", missing)):
        bi, bc, btotal, trace = rotated_binary_search(rotated, tgt)
        li, lc = linear_search(rotated, tgt)
        P("")
        P(f"4. {label}: {tgt}")
        P(dash)
        P("Rotated binary search steps (lo, hi, mid, value at mid):")
        for step in trace:
            P(f"   {step}")
        P(f"{'Algorithm':<24}{'Result':<38}{'Comparisons':<13}{'Total checks'}")
        P(f"{'Rotated Binary Search':<24}{describe(bi):<38}{bc:<13}{btotal}")
        P(f"{'Linear Search':<24}{describe(li):<38}{lc:<13}{lc}")

    # Average / worst-case comparison counts over every record in the list
    bin_counts = [rotated_binary_search(rotated, x)[1] for x in rotated]
    lin_counts = [linear_search(rotated, x)[1] for x in rotated]
    P("")
    P("5. COMPARISON COUNTS ACROSS ALL RECORDS (searching each record once)")
    P(dash)
    P(f"{'Algorithm':<24}{'Best':<8}{'Average':<10}{'Worst'}")
    P(f"{'Rotated Binary Search':<24}{min(bin_counts):<8}{sum(bin_counts) / n:<10.2f}{max(bin_counts)}")
    P(f"{'Linear Search':<24}{min(lin_counts):<8}{sum(lin_counts) / n:<10.2f}{max(lin_counts)}")

    P("")
    P("6. TIME AND SPACE COMPLEXITY")
    P(dash)
    P(f"{'Algorithm':<24}{'Time (best/avg/worst)':<30}{'Space'}")
    P(f"{'Rotated Binary Search':<24}{'O(1) / O(log n) / O(log n)':<30}O(1)")
    P(f"{'Linear Search':<24}{'O(1) / O(n) / O(n)':<30}O(1)")
    P(f"For n = {n}: log2(n) is about {math.log2(n):.2f}, so binary search needs at most "
      f"{math.ceil(math.log2(n)) + 1} halving steps,")
    P(f"while linear search may need up to {n} comparisons. Binary search stays O(log n) because each")
    P("step discards half of the list by finding which half is still sorted; both searches use only a")
    P("few index variables (no extra list), so space is O(1).")
    P(bar)

    report = "\n".join(out)
    print(report)
    with open("dispatch_search_report.txt", "w") as f:
        f.write(report)


if __name__ == "__main__":
    main()