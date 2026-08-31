import { rzpClient } from '../src/execution/executor.js';

async function checkRemoteStatus() {
  const linkId = 'plink_TWMLNbZbfzFp7C';
  const remoteRecord: any = await rzpClient.paymentLink.fetch(linkId);
  console.log('\n================ OFFICIAL RAZORPAY API RECORD ================');
  console.log(JSON.stringify(remoteRecord, null, 2));
  console.log('==============================================================\n');
}

checkRemoteStatus().catch(console.error);
