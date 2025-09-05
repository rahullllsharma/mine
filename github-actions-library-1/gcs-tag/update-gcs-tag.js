const { Storage } = require('@google-cloud/storage');
const fs = require('fs');

async function updateImageTag() {
  try {
    
    const bucketPath = process.env.BUCKET_PATH;  
    const imageTag = process.env.IMAGE_TAG;      
    const credentialsJson = process.env.GCS_SERVICE_ACCOUNT_KEY; 

    
    const credentialsPath = '/tmp/gcs-key.json';
    fs.writeFileSync(credentialsPath, credentialsJson);

    
    const storage = new Storage({
      keyFilename: credentialsPath,
    });

    
    const sourceFileName = `${imageTag}.sha`;
    const updatedFileName = `${imageTag}-updated.sha`;

   
    const bucket = storage.bucket(bucketPath);
    await bucket.file(sourceFileName).copy(bucket.file(updatedFileName));

    console.log(`Image tag updated from ${sourceFileName} to ${updatedFileName} in GCS.`);
  } catch (error) {
    console.error(`Action failed: ${error.message}`);
    process.exit(1);
  }
}

updateImageTag();
