import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
from typing import List, Dict, Tuple

class EmbeddingVisualizer:
    """Visualize embeddings in 2D/3D space."""

    @staticmethod
    def reduce_dimensions(
        embeddings: List[List[float]],
        method: str = "pca",
        dimensions: int = 2
    ) -> np.ndarray:
        """
        Reduce high-dimensional embeddings to 2D or 3D for visualization.

        Args:
            embeddings: List of embedding vectors (e.g., 384-dimensional)
            method: 'pca' or 'tsne'
            dimensions: 2 or 3

        Returns:
            Reduced embeddings as numpy array
        """
        embeddings_array = np.array(embeddings)

        if method == "pca":
            reducer = PCA(n_components=dimensions)
        elif method == "tsne":
            reducer = TSNE(n_components=dimensions, random_state=42)
        else:
            raise ValueError("Method must be 'pca' or 'tsne'")

        reduced = reducer.fit_transform(embeddings_array)
        return reduced

    @staticmethod
    def create_2d_plot(
        chunk_embeddings: List[List[float]],
        chunk_labels: List[str],
        chunk_contents: List[str],
        query_embedding: List[float] = None,
        query_text: str = "",
        retrieval_indices: List[int] = None,
        similarities: List[float] = None,
        method: str = "pca"
    ) -> go.Figure:
        """
        Create 2D visualization of embedding space.

        Args:
            chunk_embeddings: Document chunk embeddings
            chunk_labels: Labels for chunks (e.g., document names)
            chunk_contents: Preview text for chunks
            query_embedding: Optional query embedding to show
            query_text: Text of the query
            retrieval_indices: Indices of retrieved chunks
            similarities: Similarity scores for retrieved chunks
            method: Dimension reduction method ('pca' or 'tsne')

        Returns:
            Plotly figure
        """
        # Combine all embeddings for reduction
        all_embeddings = chunk_embeddings.copy()
        if query_embedding:
            all_embeddings.append(query_embedding)

        # Reduce dimensions
        reduced = EmbeddingVisualizer.reduce_dimensions(all_embeddings, method, 2)

        # Split back into chunks and query
        chunk_reduced = reduced[:len(chunk_embeddings)]
        query_reduced = reduced[-1:] if query_embedding else None

        # Create figure
        fig = go.Figure()

        # Plot document chunks
        unique_labels = list(set(chunk_labels))
        colors = px.colors.qualitative.Set2

        for i, label in enumerate(unique_labels):
            indices = [j for j, l in enumerate(chunk_labels) if l == label]
            x = [chunk_reduced[j, 0] for j in indices]
            y = [chunk_reduced[j, 1] for j in indices]
            hover_text = [
                f"<b>{chunk_labels[j]}</b><br>{chunk_contents[j][:100]}..."
                for j in indices
            ]

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                name=label,
                marker=dict(size=10, color=colors[i % len(colors)]),
                hovertext=hover_text,
                hoverinfo='text'
            ))

        # Plot query if provided
        if query_reduced is not None:
            fig.add_trace(go.Scatter(
                x=[query_reduced[0, 0]],
                y=[query_reduced[0, 1]],
                mode='markers',
                name='Query',
                marker=dict(size=20, symbol='star', color='red'),
                hovertext=f"<b>Query:</b><br>{query_text}",
                hoverinfo='text'
            ))

            # Draw lines to retrieved chunks
            if retrieval_indices and similarities:
                for idx, similarity in zip(retrieval_indices, similarities):
                    fig.add_trace(go.Scatter(
                        x=[query_reduced[0, 0], chunk_reduced[idx, 0]],
                        y=[query_reduced[0, 1], chunk_reduced[idx, 1]],
                        mode='lines',
                        line=dict(
                            color='rgba(255,0,0,0.3)',
                            width=2 + similarity * 3  # Thicker line = higher similarity
                        ),
                        hovertext=f"Similarity: {similarity:.3f}",
                        hoverinfo='text',
                        showlegend=False
                    ))

        # Update layout
        fig.update_layout(
            title=f"Embedding Space Visualization ({method.upper()})",
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            hovermode='closest',
            height=600,
            showlegend=True
        )

        return fig

    @staticmethod
    def create_similarity_heatmap(
        chunk_labels: List[str],
        similarities: np.ndarray
    ) -> go.Figure:
        """
        Create heatmap showing similarity between all chunks.

        Args:
            chunk_labels: Labels for chunks
            similarities: Similarity matrix (n_chunks x n_chunks)

        Returns:
            Plotly heatmap figure
        """
        fig = go.Figure(data=go.Heatmap(
            z=similarities,
            x=chunk_labels,
            y=chunk_labels,
            colorscale='Viridis',
            text=similarities,
            texttemplate='%{text:.2f}',
            hovertemplate='%{x} vs %{y}<br>Similarity: %{z:.3f}<extra></extra>'
        ))

        fig.update_layout(
            title="Chunk Similarity Matrix",
            xaxis_title="Chunks",
            yaxis_title="Chunks",
            height=600
        )

        return fig

    @staticmethod
    def show_vector_values(embedding: List[float], max_dims: int = 20) -> str:
        """
        Format embedding vector for display.

        Shows first N dimensions to give concrete view of what vectors look like.
        """
        if len(embedding) <= max_dims:
            values = ", ".join([f"{v:.4f}" for v in embedding])
            return f"[{values}]"
        else:
            shown = ", ".join([f"{v:.4f}" for v in embedding[:max_dims]])
            return f"[{shown}, ... ({len(embedding)} dimensions total)]"
