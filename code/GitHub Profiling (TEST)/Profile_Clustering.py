## Import Libraries
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import time
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

## Profile Clustering
df = pd.read_excel("...Profile_Data\Github_Profiles_Filtered.xlsx")
df

# Download model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Clean Data
df['top_languages'] = df['top_languages'].fillna('').astype(str)
df['common_topics'] = df['common_topics'].fillna('').astype(str)

# Combine columns
df['combined_info'] = df['top_languages'] + " " + df['common_topics']

# Define and Encode target roles
TARGET_ROLES = [
    "Data Scientist", "Data Engineer", "Solutions Architect",
    "Business Analyst", "Full Stack Developer", "Mobile Developer",
    "DevOps Engineer", "Backend Developer", "Frontend Developer",
    "Blockchain Developer", "ML Engineer", "Security Engineer"
]
role_embeddings = model.encode(TARGET_ROLES, convert_to_tensor=True)

# Process all candidates together
print("Classifying candidates...")
candidate_embeddings = model.encode(df['combined_info'].tolist(), convert_to_tensor=True, show_progress_bar=True)

# Calculate Similarity (with cos_sim)
cosine_scores = util.cos_sim(candidate_embeddings, role_embeddings)

# Find the highest scoring role for each candidate
best_role_indices = torch.argmax(cosine_scores, dim=1)
df['developer_profile'] = [TARGET_ROLES[idx] for idx in best_role_indices]

# Save file
df.to_csv('Profiles_Identified.csv')

