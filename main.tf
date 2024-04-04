provider "aws" {
  region = "ap-southeast-2"  # for Sydney region
}

resource "aws_instance" "inaturalist_data_retrieval" {
  ami           = "xxxx"  # Replace with the appropriate AMI ID
  instance_type = "t2.micro"
  key_name      = "xxxx"  # Replace with the key pair name
  
  # TODO: Configure networking and security groups
  
  tags = {
    Name = "iNaturalist Data Retrieval"
  }
}