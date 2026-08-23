# Security baseline

- Modo operacional inicial: `PAPER`.
- Segredos somente em variáveis de ambiente/server-side.
- Nunca armazenar senha bancária ou exibir credenciais completas.
- Ações sensíveis exigirão sessão autenticada, confirmação explícita, 2FA e audit log.
- Circuit breakers bloquearão novas ordens diante de dados obsoletos, drawdown excessivo, inconsistência de broker ou falhas de reconciliação.
- Nenhum segredo deve ser colocado em `NEXT_PUBLIC_*`; providers oficiais recebem credenciais apenas no backend.
- Carteira sincronizada e carteira PAPER são domínios separados e nunca devem compartilhar fallback de dados.
