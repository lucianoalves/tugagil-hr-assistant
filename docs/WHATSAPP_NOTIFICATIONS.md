# Integração de notificações com o portal

O envio WhatsApp fica no servidor Next.js do `tugaweb`; este backend Python continua responsável pela análise e gravação transacional no Supabase. Não duplicar credenciais Twilio/Meta no worker Python.

Quando `portal_finish_task` conclui uma análise de CV, `cv_finish_analysis` já gera a notificação correspondente. A migration do portal `20261010090000_whatsapp_notifications.sql` liga essa notificação à outbox WhatsApp e acrescenta a análise determinística de vagas (`job_rules`). O estado SUCCEEDED transita uma vez, evitando enfileirar duas vezes no mesmo resultado. Pedidos de IA auxiliares não geram avisos externos adicionais neste MVP.

O portal processa as outboxes WhatsApp e email após o worker responder, encaminhando para email quando WhatsApp não está disponível; o cron diário do portal também cobre conclusões do cron Python. Não fazer chamadas Twilio dentro da transação de análise: uma falha do canal não deve invalidar ou repetir o resultado do CV.

Contrato, eventos, variáveis, consentimento, setup Twilio trial/Sandbox, troca para Meta direta, tabela de custos e limitações estão em [`tugaweb/docs/WHATSAPP_NOTIFICATIONS.md`](../../tugaweb/docs/WHATSAPP_NOTIFICATIONS.md) no workspace com os dois projetos. Ao consultar este repositório isoladamente, procurar o mesmo documento no repositório `tugagil/tugaweb`.

O login é código por email, independente destes providers. Segredos são configurados no ambiente do projeto Vercel `tugagil-members`; não em Git.
