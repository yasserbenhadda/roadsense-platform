import { Module } from '@nestjs/common';
import { ProcessingService } from './processing.service';
import { MinioModule } from '../minio/minio.module';
import { ConfigModule } from '@nestjs/config';

@Module({
    imports: [MinioModule, ConfigModule],
    providers: [ProcessingService],
    exports: [ProcessingService],
})
export class ProcessingModule { }
