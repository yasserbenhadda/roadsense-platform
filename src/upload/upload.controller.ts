import {
    Controller, Post, UploadedFile, UseInterceptors, BadRequestException
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { Express } from 'express';
import { UploadService } from './upload.service';



@Controller('uploadVideo')
export class UploadController {
    constructor(private readonly uploadService: UploadService) { }

    @Post()
    @UseInterceptors(FileInterceptor('file'))
    async upload(
        @UploadedFile() file: any,
    ): Promise<{ jobId: string; message: string }> {

        // 1. Vérifier extension
        if (!file?.originalname.endsWith('.mp4')) {
            throw new BadRequestException("Le fichier doit être un .mp4");
        }

        // 2. Envoyer au service
        const jobId = await this.uploadService.handleUpload(file);

        return {
            jobId,
            message: "Video uploaded, processing started"
        };
    }
}