
import os
import sys

def estimate_tokens(text):
    return len(text) / 4

def run_test(control_path, variant_path):
    if not os.path.exists(control_path) or not os.path.exists(variant_path):
        print(f"Error: Files not found.\nControl: {control_path}\nVariant: {variant_path}")
        return

    with open(control_path, 'r') as f:
        control = f.read()
    with open(variant_path, 'r') as f:
        variant = f.read()
        
    t_control = estimate_tokens(control)
    t_variant = estimate_tokens(variant)
    
    diff = t_variant - t_control
    pct = (diff / t_control) * 100
    
    print(f"--- A/B Test Results ---")
    print(f"Files: {os.path.basename(control_path)} vs {os.path.basename(variant_path)}")
    print(f"Control (v3.5): ~{t_control:.0f} tokens")
    print(f"Variant (v3.6): ~{t_variant:.0f} tokens")
    print(f"Delta: {diff:+.0f} tokens ({pct:+.2f}%)")
    
    if pct < 0:
        print("RESULT: PASS (More efficient)")
    elif pct < 5:
         print("RESULT: PASS (Acceptable overhead for better structure)")
    else:
        print("RESULT: WARNING (Significant overhead)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tests/ab_test_generic.py <control_path> <variant_path>")
    else:
        run_test(sys.argv[1], sys.argv[2])
