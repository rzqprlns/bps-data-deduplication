# Large-Scale Data Cleaning & Deduplication

> A Python-based data cleaning and deduplication workflow developed from my experience processing large-scale data at **BPS Kota Bogor**.

**191K+ records processed · 46K+ duplicate records removed · Python**

> **Data Privacy**
> This repository uses fully synthetic data. No confidential, identifiable, or original BPS data is included.

---

## Project Overview

During my work as a Statistical Assistant at BPS Kota Bogor, I worked with a dataset containing more than **191,000 records** that required address standardization and duplicate removal.

The main challenge was that the same information could appear in different formats, especially in address fields. The large size of the dataset also made duplicate detection computationally heavier.

I developed a Python-based workflow to:

- standardize inconsistent name and address formats;
- identify duplicate records based on **name, address, and name + address**;
- partition records by **kecamatan** before duplicate processing;
- retain one representative record from each duplicate group; and
- remove **46,000+ redundant duplicate records**.

---

## Project at a Glance

| | |
|---|---|
| **Dataset Size** | 191K+ records |
| **Duplicates Removed** | 46K+ records |
| **Data Format** | CSV |
| **Language** | Python |
| **Libraries / Methods** | Pandas · Regex |
| **Focus** | Data Cleaning · Deduplication · Data Quality |

---

## The Problem

One of the main issues was inconsistent address formatting.

The same address could be written in several different ways:

```text
Jl. Pajajaran No. 10 RT 1/RW 5

Jalan Pajajaran Nomor 10 RT 01 RW 05

JL PAJAJARAN NO 10 RT01 RW05
```

Although these records may refer to the same address, Python initially reads them as different strings.

Therefore, the data needed to be standardized before duplicate detection could be performed reliably.

---

## Workflow

```text
                     RAW CSV
                   191K+ RECORDS
                         │
                         ▼
              ┌─────────────────────┐
              │ DATA STANDARDIZATION│
              │   Name & Address    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │     PARTITION       │
              │   BY KECAMATAN      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ DUPLICATE DETECTION │
              └──────────┬──────────┘
                         │
                ┌────────┼────────┐
                ▼        ▼        ▼
              NAME    ADDRESS   NAME +
                                ADDRESS
                │        │        │
                └────────┼────────┘
                         ▼
              ┌─────────────────────┐
              │  DUPLICATE GROUPS   │
              └──────────┬──────────┘
                         │
                         ▼
              KEEP 1 REPRESENTATIVE
                    PER GROUP
                         │
                         ▼
                 CLEAN DATASET
```

---

# 01 — Data Standardization

Before searching for duplicates, the raw text was standardized using Python.

The cleaning process handled variations such as:

- `Jl.`, `JL`, `Jln.` → `JALAN`
- inconsistent house-number notation;
- inconsistent RT/RW formatting;
- capitalization differences;
- punctuation;
- extra whitespace.

### Example

**Before**

```text
Jl. Flamboyan No. 247 RT 13/RW 3
```

**After**

```text
JALAN FLAMBOYAN NOMOR 247 RT 13 RW 03
```

This process makes records with different writing styles easier to compare consistently.

---

# 02 — Partitioning by Kecamatan

Processing duplicate candidates across a large dataset can increase computational workload.

Instead of processing all **191K+ records** together, I divided the dataset by **kecamatan** before running duplicate detection.

```text
                    FULL DATASET
                         │
                         ▼
                GROUP BY KECAMATAN
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    KECAMATAN A    KECAMATAN B    KECAMATAN C
          │              │              │
          ▼              ▼              ▼
      DUPLICATE      DUPLICATE      DUPLICATE
      DETECTION      DETECTION      DETECTION
```

### Why?

The working assumption was that duplicate records were most likely to occur within the same kecamatan.

This reduced the amount of data processed together and made the workflow more manageable.

### Trade-off

This strategy also introduces a limitation:

> A duplicate recorded under different kecamatan could potentially be missed.

This assumption is therefore treated as a processing strategy rather than a guarantee that cross-district duplicates do not exist.

---

# 03 — Duplicate Detection

After standardization and partitioning, duplicate records were identified using three main checks:

| Rule | Comparison |
|---|---|
| **01** | Name |
| **02** | Address |
| **03** | Name + Address |

Duplicate groups could contain different numbers of repeated records.

For example:

```text
GROUP A

Record 01 ──┐
Record 02   │
Record 03   ├── Same entity
Record 04 ──┘

Keep   → 1 record
Remove → 3 redundant records
```

Another group might contain only two records:

```text
GROUP B

Record 01 ──┐
Record 02 ──┘  Same entity

Keep   → 1 record
Remove → 1 redundant record
```

The objective was not to remove every record belonging to a duplicate group.

Instead:

> **One representative record was preserved, while the remaining redundant copies were removed.**

---

# 04 — Results

| Metric | Result |
|---|---:|
| Records processed | **191K+** |
| Redundant duplicates removed | **46K+** |
| Representative record | **1 per duplicate group** |
| Processing strategy | **Partition by kecamatan** |

The final workflow preserved unique records while removing redundant copies from duplicate groups.

---

# 05 — Synthetic Dataset

The original dataset used during the work at BPS Kota Bogor is **not included in this repository**.

Instead, this project provides a synthetic dataset that recreates similar data-quality problems.

The demo dataset contains:

- inconsistent street-name formatting;
- different RT/RW formats;
- different house-number formats;
- variations in business-name formatting;
- duplicate groups of different sizes;
- unique records; and
- kecamatan information.

This allows the workflow to be demonstrated publicly without exposing institutional data.

---

# 06 — Live Demo

An interactive version of the project is currently being developed.

The demo will allow users to:

1. explore raw synthetic data;
2. run address standardization;
3. compare before vs. after cleaning;
4. detect duplicate records;
5. inspect duplicate groups; and
6. view the resulting clean dataset.

### Live Demo

**Coming soon →**

---

# Tech Stack

`Python` · `Pandas` · `Regex` · `CSV`

---

# Repository Structure

```text
bps-data-deduplication/
│
├── README.md
├── app.py
├── requirements.txt
│
├── data/
│   └── synthetic_data.csv
│
├── src/
│   ├── cleaning.py
│   └── deduplication.py
│
└── assets/
```

---

# About This Project

This repository is a portfolio reconstruction of a data-cleaning and deduplication workflow I worked on as a **Statistical Assistant at BPS Kota Bogor**.

The public implementation focuses on demonstrating the **problem-solving process, data-cleaning logic, processing strategy, and technical implementation** without publishing the original institutional dataset.

---

### Rizqi Aprilianes

**Data Analysis · Data Quality · Automation**

`Python` `Pandas` `Excel` `Google Apps Script`
