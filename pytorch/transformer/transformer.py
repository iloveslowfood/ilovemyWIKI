import torch
from torch import nn

from encoder import Encoder
from decoder import Decoder
from positional_encoding import PositionalEncoder


class Transformer(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        max_len: int,
        d_model: int,
        num_heads: int,
        num_encoders: int = 1,
        num_decoders: int = 1,
    ):
        """Transformer for Machine Translation

        Args:
            vocab_size (int): 임베딩 딕셔너리 사이즈
            max_len (int): 문장의 최대 길이(최대 토큰 수)
            hidden_dim (int): 인코더, 디코더 내 hidden state의 차원. 입력 데이터에 대한 임베딩 차원과 같음
            num_heads (int): Attention 헤드 수
            num_encoders (int): 인코더 블록 수
            num_decoders (int): 디코더 블록 수
        """
        super(Transformer, self).__init__()
        self.d_model = d_model
        self.max_len = max_len

        self.embedder = nn.Embedding(
            num_embeddings=vocab_size, embedding_dim=d_model
        )
        self.positional_encoder = PositionalEncoder(d_model=d_model)
        self.encoders = self._get_encoders(num_encoders=num_encoders)
        self.decoders = self._get_decoders(num_decoders=num_decoders)
        self.linear = nn.Linear(in_features=d_model, out_features=vocab_size)
    

    def forward(self, input: torch.Tensor, output: torch.Tensor) -> torch.Tensor:
        input_embedded = self._get_embedding_with_positional_encoding(input)
        output_embedded = self._get_embedding_with_positional_encoding(output)

        enc_hidden_state = input_embedded.clone()
        for encoder in self.encoders:
            enc_hidden_state = encoder(enc_hidden_state)

        dec_hidden_state = output_embedded.clone()
        for decoder in self.decoders:
            dec_hidden_state = decoder(
                encoder_hidden_state=enc_hidden_state, output_embedded=dec_hidden_state
            )

        output = self.linear(dec_hidden_state)
        return output


    def _get_encoders(self, num_encoders: int) -> nn.Sequential:
        encoders = [
            Encoder(d_model=self.d_model, num_heads=self.num_heads, max_len=self.max_len)
            for _ in range(num_encoders)
        ]
        return nn.Sequential(*encoders)
    

    def _get_decoders(self, num_decoders: int) -> nn.Sequential:
        decoders = [
            Decoder(d_model=self.d_model, num_heads=self.num_heads) for _ in range(num_decoders)
        ]
        return nn.Sequential(*decoders)


    def _get_embedding_with_positional_encoding(self, input: torch.Tensor) -> torch.Tensor:
        input_embedded = self.embedder(input)
        input_embedded += self.positional_encoder(max_len=self.max_len)
        return input_embedded

