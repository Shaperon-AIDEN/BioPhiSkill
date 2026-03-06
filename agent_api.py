import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from abnumber import Chain
from biophi.humanization.methods.humanness import get_antibody_humanness, OASisParams

def evaluate_and_plot_humanness(vh_seq=None, vl_seq=None, 
                                oasis_api_url="https://biophioasisapi.azurewebsites.net/api/peptides/", 
                                min_fraction_subjects=0.1,
                                output_dir="output"):
    """
    Evaluates the humanness of the given VH and/or VL sequences using the OASis Azure API,
    and generates an Excel report and a Matplotlib/Seaborn plot of the peptide humanness profiles.
    """
    if not vh_seq and not vl_seq:
        raise ValueError("At least one of vh_seq or vl_seq must be provided.")

    os.makedirs(output_dir, exist_ok=True)
    
    vh_chain = Chain(vh_seq, scheme="imgt") if vh_seq else None
    vl_chain = Chain(vl_seq, scheme="imgt") if vl_seq else None
    
    params = OASisParams(
        oasis_db_path=oasis_api_url,
        min_fraction_subjects=min_fraction_subjects
    )
    
    print("Evaluating humanness via OASis API...")
    res = get_antibody_humanness(vh=vh_chain, vl=vl_chain, params=params)
    
    # 1. Save Excel Report
    df = res.to_peptide_dataframe()
    excel_path = os.path.join(output_dir, "humanness_report.xlsx")
    df.to_excel(excel_path, index=False)
    
    # 2. Visualization
    sns.set_theme(style="whitegrid")
    
    chains_to_plot = []
    if vh_chain: chains_to_plot.append(('Heavy', res.vh))
    if vl_chain: chains_to_plot.append(('Light', res.vl))
    
    fig, axes = plt.subplots(len(chains_to_plot), 1, figsize=(12, 5 * len(chains_to_plot)), squeeze=False)
    
    for i, (chain_name, chain_res) in enumerate(chains_to_plot):
        chain_df = chain_res.to_peptide_dataframe()
        # Ensure 'Fraction OAS Subjects' is available and handle NaNs
        chain_df['OASis Percentile'] = chain_df['Fraction OAS Subjects'].fillna(0) * 100
        
        # Use string representation of positions for the x-axis to maintain order
        x_labels = [str(pos) for pos in chain_df.index]
        
        ax = axes[i][0]
        sns.barplot(x=x_labels, y=chain_df['OASis Percentile'], ax=ax, color="royalblue")
        
        # Highlight non-human peptides (red)
        threshold_percentage = min_fraction_subjects * 100
        ax.axhline(threshold_percentage, color='red', linestyle='--', label=f'Threshold ({threshold_percentage}%)')
        
        ax.set_title(f"{chain_name} Chain Peptide Humanness Profile", fontsize=14)
        ax.set_xlabel("Peptide Start Position (IMGT)", fontsize=12)
        ax.set_ylabel("OASis Subject %", fontsize=12)
        ax.set_ylim(0, 100)
        ax.legend()
        
        # Sparse x-ticks to prevent overlapping
        xticks = ax.get_xticks()
        ax.set_xticks(xticks[::5])
        ax.set_xticklabels([x_labels[idx] for idx in xticks[::5]], rotation=45)
        
    plt.tight_layout()
    plot_path = os.path.join(output_dir, "humanness_plot.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    oasis_id = res.get_oasis_identity(min_fraction_subjects) * 100
    print(f"Evaluation complete. OASis Identity: {oasis_id:.2f}%")
    print(f" - Excel Report: {excel_path}")
    print(f" - Plot Image: {plot_path}")
    
    return {
        "num_peptides": res.get_num_peptides(),
        "num_human_peptides": res.get_num_human_peptides(min_fraction_subjects),
        "oasis_identity": oasis_id,
        "excel_report": excel_path,
        "plot_image": plot_path
    }

if __name__ == "__main__":
    # Example usage for testing when running this script directly
    example_vh = "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS"
    
    # We will mock the Chain slightly if abnumber ANARCI parsing fails, but normally users will pass a valid seq
    try:
        evaluate_and_plot_humanness(vh_seq=example_vh, output_dir="example_output")
    except Exception as e:
        print(f"Error during example execution: {e}")
