from Name_State_DB_Lookup import lookup_firm, format_firms_output

test_cases = [
    ('Christopher Ruggiero', 'NE'),
    ('Chris Ruggiero', 'NE'),
    ('Christoph Ruggiero', 'NE'),  # Slight misspelling (fuzzy)
    ('Edward Kitchell', 'NY'),
    ('Ed Kitchell', 'NY')
]

print("=== Running Verification Tests on 2D Partitioned Database ===")
for name, state in test_cases:
    recs, score, m_name = lookup_firm(name, state)
    firms = format_firms_output(recs)
    print(f"Input: ({name:20s}, {state}) -> Match: {str(m_name):20s} (Score: {score:5.1f}%) | Firm: {firms}")
