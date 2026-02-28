from transformers import GPT2Config, GPT2LMHeadModel

def build_model(vocab_size, block_size):
    config = GPT2Config(
        vocab_size=vocab_size,
        n_positions=block_size,
        n_ctx=block_size,
        n_embd=512,
        n_layer=6,
        n_head=8,
        resid_pdrop=0.1,
        embd_pdrop=0.1,
        attn_pdrop=0.1
    )

    model = GPT2LMHeadModel(config)
    return model