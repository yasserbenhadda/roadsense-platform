import { Module } from '@nestjs/common';
import { UploadController } from './upload.controller';
import { UploadService } from './upload.service';
import { ProcessingModule } from '../processing/processing.module';

@Module({
  imports: [ProcessingModule],
  controllers: [UploadController],
  providers: [UploadService]
})
export class UploadModule { }
