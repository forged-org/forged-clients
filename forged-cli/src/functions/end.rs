use cynic::MutationBuilder;

use crate::{queries::FinishRun, Result};

pub async fn end(client: &mut forged::Client) -> Result<()> {
    eprintln!("Finishing current device ...");
    client.run_query(FinishRun::build(())).await?;

    Ok(())
}
